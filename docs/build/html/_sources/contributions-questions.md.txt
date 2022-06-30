# Contributions
## Would you like to help with writing code for this project?
We need help to maintain and improve this code. How can you help?

Archives are constantly changing their file transfer protocols. If you find one in gnssrefl that doesn't work anymore, please fix it and let us know. Please test that it works for both older and newer data.

If you would like to add an archive, please do so. Use the existing code in gps.py as a starting point.

We need better models for GNSS-IR far more than we need more journal articles finding that the method works. And we need these models to be in python.

I would like to add a significant wave height calculation to this code. If you have such code that works on fitting the spectrum computed with detrended SNR data, please consider contributing it.

If you have a better refraction correction than we are using, please provide it to us as a function in python.

Write up a new use case.

Investigate surface related biases for polar tide gauge calculations (ice vs water).

I have ported NOCtide.m and will add it here when I get a chance.

# Questions
##  How to get help with your gnssrefl questions
If you are new to the software, you should consider watching the videos about GNSS-IR

Before you ask for help - a few things to ask yourself:

Are you running the current software?

gnssrefl command line - git pull

gnssrefl docker command line - docker pull unavdocker/gnssrefl

gnssrefl jupyter notebook - git pull

gnssrefl jupyter notebook docker- docker pull unavdocker/gnssrefl_jupyter

You are encouraged to submit your concerns as an issue to the github repository. If you are unfamiliar with github, you can also email Kelly (enloe@unavco.org ) about Jupyter NoteBooks or Tim (dittmann@unavco.org) for commandline/docker issues.

Please

include the exact command or section of code you were running that prompted your question.

Include details such as the error message or behavior you are getting. Please copy and paste (this is preferred over a screenshot) the error string. If the string is long - please post the error string in a thread response to your question.

Please include the operating system of your computer.

Would you like to join our gnssrefl users email list? Send an email to gnss-ir-request@postal.unavco.org and put the word subscribe (or unsubscribe to leave) in your email subject.


