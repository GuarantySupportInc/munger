# Munger

## Overview

This project is a schema-based approach to converting CSVs from a source format to the target format, be that UDS, OLCP, or otherwise.

It is built on top of the Cerberus project: https://docs.python-cerberus.org/en/stable/

While Cerberus is mainly for validation, it has the ability to "coerce", or transform, data to make it fit validations. Inspired by that, I 
made this project to combine the three steps we usually take on insolvency data into one piece of software.

Those steps are:

1. Filtering -- Narrowing down the source file to the rows we want.
2. Coercion -- Transforming the data to our target format.
3. Validation -- Confirming the data matches our expectations for the target format.

You define a schema as a Python dict for one or more of these steps, register them to the Munger instance, register one or more output files, 
then run munge_all().

It aims to be flexible. You may run a munger instance with only a filter to get the open claims out of the source file. Or you may run only a 
validation, to see how many things are wrong with the source file that you'll need to fix in coercion. You may also register writers to certain 
"hooks", so that lines that fail validation are output to their own file for further investigation while lines that pass move on to the cleaned file. Etc.

Several coercions are predefined, as given in the Cerberus documentation, and I added many more general ones for UDS/OLCP use in the coercions.py file.
Even beyond that, you can define custom coercions and even custom Validators to further extend what sorts of cleanups Munger can do.

## Unfinished

Unforutnately, this project never quite made it out of alpha. It was functional enough to run cleanup for some Lighthouse and Gulfstream files, but not fully robust
or finalized enough for me to sit down and write out full documentation.

The largest disadvantage is that it is very slow, compared to an ad hoc cleanup script. I believe this to be a limitation of the underlying Cerberus
package. It's my deepest regret that I didn't dig into and improve the efficiency, because I really believe a schema-based approach to insolvency data
cleanup would be _worlds_ more readable and understandable than our current methods of scattered scripts and detached documentation.

I pass this repo onto Guaranty Support Inc because it is used as a package in some historic insolvencies, and may be needed again in the future. I wrote
the script in my personal time but only used it for company purposes, and rather than deal with the legal confusion of that, I donate it to you. If you
find this package useful in your future endeavors, I will be happy. If you further develop it, I might cry tears of pride. Regardless, farewell Munger.
You had a terrible name.

- Doug

<3 - Nate
