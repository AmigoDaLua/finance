# This is CS50’s Finance
This is Finance, from Harvard’s CS50 Problem Set 9.

## The beginning
If you’d asked me about it 3 months ago, when "print("hello, world")" was my greatest achievement in programming, I woudn’t believe it, but here we are. 
After a lot of reading, learning, failing and trying again and again, I’ve succesfully programmed a web app using Python, SQL, HTML, CSS and Flask!

### The app
Finance is a web application that uses real stock info to let you “buy” and “sell” stocks with fictional money. 
The app is capable of finding out the actual quotation of the stocks thanks to [IEX Exchange](https://exchange.iex.io/products/market-data-connectivity/) information,
and all the transactions are made using such values, like the real ones .

## The challenge
This is one of the CS50’s latest modules, so here it’s all about putting together a ton of knowledge (and it’s awesome).

Here I am using Python language and it's web development framework Flask to build a complete web application that consults real prices, buys and sells (fake) stocks and, 
thanks to SQLite3, stores all the user's info on a safe database. 
Each one of the app's screens corresponds to a HTML page that uses CSS for great looks.

### Implementation

The challenge was to implement 6 functions, each one responsable for one of the app's features.

* In **Register**, a new user is registered in the database (if the username is not already taken, of course)

<img
  src="/img/register.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  

* **Quote** allows users to discover the actual quotation of any valid stock

<img
  src="/img/quote.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  
  
<img
  src="/img/quoted.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">

* In **Buy** users can spend some ficctional money on new stocks

<img
  src="/img/buy.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  

* In **Sell**, users can have it’s fake cash back by selling some stocks

<img
  src="/img/sell.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  

* The **Index** page shows all of the stocks they currently own

<img
  src="/img/index.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">


* **History** shows all the transactions made by the user

<img
  src="/img/history.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  

#### Personal touch
The last feature I've had to implement was my personal touch, so I chose to add two small but meaningful features:

* For security, user’s passwords must have at least 6 characters and at least 1 special character. Thanks to this piece of code:

        elif len(request.form.get("password")) < 6: # password must have at least 6 characters
            return apology("password must have at least 6 characters")

        elif request.form.get("password").isalnum() == True: # password must have at least 1 special character
            return apology("password must contain at least 1 special character")
            
* On “Buy” and “Quote” pages, people who don’t know a lot about the stocks market and their symbols (like myself) can feel a little more at home by clicking on the suggested link. 
It will show trending stocks from [Stock Analysis](https://stockanalysis.com/) so users can find out it’s favorite company’s symbol.

<img
  src="/img/quote_exemplo.png"
  alt="Index page"
  style="display: inline-block;  padding: 10px; max-width: 300px">
  
## Last words
I've really learned a lot about programming and web development while I was making this app. It was magical to see that with persistence, good guidance and lots of hardwork, things that seemed impossible or obscure can come to light and, at some point (after days of agony), work properly! 

Even if they are (in)visible enigmas on your computer's screen today, tomorrow, if you try your best, everything may just work out.






