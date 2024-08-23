# stackvlass
Utilities for stacking Very Large Array Sky Survey quick-look images using htcondor

These files should allow you to image-plane stack a set of 1deg^2 VLASS subtiles over three epochs and produce:

1. Stacked image
2. RMS image
3. Source catalog of stacked image
4. Source catalog of single-epoch images.

## Workflow

### Selecting tiles or subtiles to stack
Begin by identifying a set of tiles or subtiles that you wish to stack. A set of tiles will be more useful for final catalog creation, but will statistically be affected by variables such as weather, ionosphere, etc.
Using a random set of subtiles is recommended for a more robust sample when testing survey properties.
I have provided one such set, randomsubtiles.fits, which contains a roughly even distribution of 67 subtiles on the sky. 
As of August 2024 not all these had been observed in three epochs, and my tests were only done on 58 of them. 
However, by October of 2024, barring data processing errors all these subtiles should be processed.

If you have a list of tiles you would like to stack, use "makedatabase.py" and put the VLASS tile names in the set defined on line 4.
On the other hand, if you have a list of subtiles, you will need a file with the names of these subtiles and their corresponding tiles, formatted like "randomsubtiles.fits". Then, use "databasefromsubtile.py" and enter your file's name on line 7.
Both these creation files do not write to an output file and instead simply list the appropriate URLs to stdout.
This is because I was lazy, and you are welcome to submit a pull request fixing this.
Until you do, however, simply use "python (filename.py) > (outputfile.txt)" to save to a file.
I used a file called "output.txt", and you will see this name pop up in other files in this repository. If you use a different file simply substitute that file's name.

### Setting things up with htcondor

I did my stacking using the University of Wisconsin's Center for High Throughput Computing (CHTC), and there are some parts of this code that are customised for that location specifically.
I will attempt to point these out as I go but may miss some.

These scripts work as follows with htcondor: Given a list of subtiles to stack, we use one core for each subtile and process each in parallel. Assuming the number of available cores is as large as the number of subtiles to stack, any number of subtiles can be stacked in the same amount of time as a single one.
To accomplish this we need to use containers. I used Apptainer, but Docker may be able to work as well with minimal changes to this code.
The definition file for the container is "container.def". You will need to submit an interactive job in order to make this container, and should follow the relevant instructions for your software and computing cluster to do so.
In the end you should have a .sif file, which is your container. In my tests I put this file in the CHTC /staging/ directory, but consult your local sysadmin or guide for what their preference is.
Point to your container in the submit file using htcondor's "container_image" parameter.

### Submitting the jobs

On the CHTC, the "submit.sub" file should work almost out of the box once you have built your container, you will need to change the container image location for sure though.
Rather than use htcondor's "transfer_image_files" command, we simply have the cores excecute a wrapper file that will parse the correct line of "output.txt" (change if you need to), `wget` the appropriate files, run the stacking procedure, and delete unneeded data by-products afterward.
A previous version of this code did use the condor file transfer utility, which is overall preferable performance-wise. However this procedure failed when queueing more than one process for unknown reasons, which I believe could be due to a bug.
The CHTC helpdesk has been (very slowly) investigating the problem for me but as wget works perfectly fine you can just use the procedure in "stack_wrapper.sh". If they get back to me I may update this code but as this project has been deemed "not conducive to a Ph.D" I probably will not bother.

Anyway, once you've made the requisite changes to the submission file, you can go ahead and use condor_submit to run it. The last line of the submit file, "queue n" dictates how many subtiles you'll run at once. 
I recommend n=1 for intial testing, n=2 once that's done to make sure you can run multiple jobs at once and to check that they are indeed separate subtiles, and n=(number of lines in output.txt) to actually do the job.
Be aware that at least for CHTC people start to get suspicious when you run more than a thousand jobs at once, so perhaps stick to smaller batches (or even better, get in contact with them to see what special procedures you must take).

### Data Products

Each instance of these scripts (i.e. each subtile) will produce nine data products, the first two being the actual stacked image and its rms image (produced using pybdsf), the next three being native-resolution quick-look imaging catalogs for each of the single epoch images, the following three being the same catalogs for quick-look images that have been convolved to the same resolution as your stack, and the final being the catalog of the stacked image itself.
The images and catalogs are named in a way that follows that of the VLASS quick-look image system, and should be fairly easy to identify.
You will need to concatenate the catalogs in order to use them in a sensible way. "concat.py" will work for this, but needs some preliminary processing first.
To use, you must have all the catalogs in the same directory. Then, make seven directories: "epoch1", "convolved_epoch1", "epoch2", (etc), and "stack". Next, move all the catalog files into the correct folder - this should be pretty easy with unix wildcards. Finally, run "concat.py" from the directory one level up from these folders you just created, and you will recieve seven catalogs, once from each folder.
Note that these catalogs will probably contain duplicates if you stacked adjacent subtiles. If you plan to make a real data release using this code you will need to deal with that.

Use the "convolved" single-epoch catalogs for comparing to the stacked images, especially when dealing with fluxes. Due to PSF sampling comparing fluxes with the unconvolved catalogs will not work.
The non-convolved single-epoch images are suitable for detecting when the stack blends multiple components, or for variability. Really the possibilities are endless.

## Final Notes

Thanks for reading this file. If you are interested in actually making data products using image-plane stacked quick-look vlass images feel free to get in touch with me.
