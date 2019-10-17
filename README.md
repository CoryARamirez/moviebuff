#MovieBuff

In order to run the application, please do the following:

* Ensure you have Vagrant and Virtualbox installed.
* Navigate to the [FSND VM Repo](https://github.com/udacity/fullstack-nanodegree-vm) and follow the provided instructions
to get a vagrant machine up and running.
* If the above has already been configured, you may run:
    * `vagrant up` to provision and bring your VM online, then;
    * `vagrant ssh` to ssh into the machine.
* Once inside, navigate to: `/vagrant/catalog`.
* Enter the command `python application.py` to start the application.
---
If the application boots up successfully, you will see an output similar to:
```
vagrant@vagrant:/vagrant/catalog$ python application.py
Seeded database with default movie categories and items!
 * Serving Flask app "application" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
Seeded database with default movie categories and items!
 * Debugger is active!
 * Debugger PIN: 3`25-904-188
```
You may now open your browser and navigate to: `http://localhost:5000/` to begin viewing and using the application.

#### Note: the application uses Google's OAuth flow for authentication and is required.