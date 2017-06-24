# Web2Py SparkPost Plugin

## Why?

I've seen a lot of people integrating web2py with SparkPost using SMTP instead of the REST API, mainly so Auth also works correctly.  
  
I would like to be able to use SparkPost without changing any of my mail sending code in a project. This plugin is designed so you can keep sending emails exactly the same way you always did with web2py.   
  
Finally, I also wanted to start using SparkPost in my web2py projects, so here we are.  
  
## Installation

Just copy plugin_sparkpost.py file into your application's modules folder.

## Usage

A simple way to use would be to put this in one of your model files (usually db.py):

    from plugin_sparkpost import SparkMail
    mail = SparkMail(api_key='YOUR_API_KEY_HERE', sender='no-reply@example.com')

    auth = Auth(db, host_names=myconf.get('host.names'), mailer=mail)

## Dependencies

- [python-sparkpost](https://github.com/SparkPost/python-sparkpost): SparkPost official python package, you can just put the sparkpost folder in your application modules folder if you want.

## Differences to web2py's default mailer

This plugin does not support raw or encrypted email.

## License

MIT
