Boxy on OpenShift
===================

Running on OpenShift
----------------------------

Create an account at https://www.openshift.com/

Create a python application based on the code in this repository

    rhc app create boxy python-3.3 --from-code https://github.com/shouxi/boxy.git

That's it, you can now checkout your application at:

    http://boxy-$yournamespace.rhcloud.com