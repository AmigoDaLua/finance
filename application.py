import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db") # <<<< A DATABASE!

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    # getting user id
    owner_id = session["user_id"]

    # getting user stocks
    rows = db.execute("SELECT stock_symbol, SUM(shares) FROM transactions WHERE owner_id = ? GROUP BY stock_symbol HAVING SUM(shares) > 0", owner_id)

    # getting user cash
    user_cash = round(db.execute("SELECT cash FROM users WHERE id = ?", owner_id)[0]["cash"], 2)

    # list to store the stocks
    stocks = []
    total_cash = 0

    for row in rows: # popullating the stocks list with info
        stock = lookup(row["stock_symbol"])
        shares_value = stock["price"] * row["SUM(shares)"]
        total_cash += shares_value
        stocks.append({"name": stock["name"],"symbol":stock["symbol"], "shares":row["SUM(shares)"], "price":usd(stock["price"]), "shares_value":usd(shares_value)})

    total_cash = user_cash + total_cash

    return render_template("index.html", stocks=stocks, total_cash=usd(round(total_cash, 2)), user_cash=usd(user_cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "POST":

        # checking if symbol is valid
        if not request.form.get("symbol") or lookup(request.form.get("symbol")) == None:
            return apology("Invalid stock symbol", 400)

        # checking if shares is valid
        elif not request.form.get("shares") or int(request.form.get("shares")) <= 0:
            return apology("Invalid share(s) amount", 400)

        # checking if user has cash
        owner_id = session["user_id"]
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", owner_id)[0]["cash"]

        # stock info
        stock = lookup(request.form.get("symbol"))
        stock_price = float(stock["price"])
        stock_symbol = stock["symbol"]

        shares = int(request.form.get("shares"))

        total_price = stock_price * shares

        # testing if user has enough cash
        if float(user_cash) < total_price:
            apology("Sorry, not enough cash", 400)

        elif float(user_cash) >= total_price:
            # updating cash
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash - total_price, owner_id)
            db.execute("INSERT INTO transactions (owner_id, stock_symbol, stock_price, shares, operation, datetime) VALUES(?,?,?,?,?,datetime('now', 'localtime'))", owner_id, stock["symbol"], stock["price"], shares, "PURCHASE")
            # updating database
        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():

    # getting user id
    owner_id = session["user_id"]

    # getting user stocks
    stocks = db.execute("SELECT stock_symbol, stock_price, shares, operation, datetime FROM transactions WHERE owner_id = ?", owner_id)

    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"): # <<< se username está VAZIO
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "GET":
       return render_template("quote.html")

    else:
        symbol = request.form.get("symbol")

        if not symbol: # is symbol valid?
            return apology("No stock symbol", 400)

        else:
            quotation = lookup(symbol)

            if quotation == None: # checking if there's a quotation
                return apology("Invalid stock symbol", 400)

            else:
                return render_template('quoted.html',
                stock={ # sending stock info to HTML
            'name': quotation['name'],
            'symbol': quotation['symbol'],
            'price': usd(quotation['price'])
            })


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensuring that pass and confirm are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password confirmation is wrong", 400)

        # special password requests!

        elif len(request.form.get("password")) < 6: # password must have at least 6 characters
            return apology("password must have at least 6 characters")

        elif request.form.get("password").isalnum() == True: # password must have at least 1 special character
            return apology("password must contain at least 1 special character")

        else:
            username = request.form.get("username")
            h_password = generate_password_hash(request.form.get("password"))

            try: # dealing with duplicated usernames
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, h_password)
                return redirect("/")
            except:
                return apology("username already taken", 400)

    else:
        return render_template("/register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():


    if request.method == "POST":

        owner_id = session["user_id"]
        stock = lookup(request.form.get("symbol"))

        # check if symbol exists
        if stock == None:
            return apology("Invalid symbol", 400)

        # check if shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Shares must be a positive integer", 400)

        user_shares = db.execute("SELECT SUM(shares) as total_shares FROM transactions WHERE owner_id = ? AND stock_symbol = ? GROUP BY stock_symbol HAVING SUM(shares) > 0", owner_id, stock["symbol"])[0]["total_shares"]

        # user has enough shares?
        if shares > user_shares:
            return apology("Not enough shares")

        elif not db.execute("SELECT stock_symbol FROM transactions WHERE owner_id = ? AND stock_symbol = ?", owner_id, request.form.get("symbol")):
            apology("Invalid stock", 403)

        # query database for user's cash
        user_cash = float(db.execute("SELECT cash FROM users WHERE id = ?", owner_id)[0]["cash"])

        # share cost
        price_per_share = stock["price"]

        # calculate the price of requested shares
        total_price = price_per_share * shares

        # updating user's cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + total_price, owner_id)
        # recording transaction on database
        db.execute("INSERT INTO transactions (owner_id, stock_symbol, stock_price, shares, operation, datetime) VALUES(?,?,?,?,?,datetime('now', 'localtime'))", owner_id, stock["symbol"], stock["price"], -shares, "SALE")

        flash("Sold!")

        return redirect("/")

    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
