"""Create a summary HTML page of GBT pipeline-produced images.

"""

import glob
import os.path
import argparse
import sys

from jinja2 import Template
from kapteyn import maputils
from matplotlib import pylab as plt
import matplotlib.gridspec as gridspec

# parse the command line to look for an input directory
def get_command_line_args(argv):
    """Read the command line arguments

    """

    if len(argv) == 1:
        argv.append("-h")

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str,
                        help="Directory path containing pipeline images.")
    args = parser.parse_args()
    return args

def create_images(directory):
    """Create PNG images for every 'cont' image in the directory

    """

    # create a directory for output images
    image_dir = './images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # look for all 'cont' files in given directory
    for fname in glob.glob(directory + '/*_cont.fits'):

        print 'processing file', fname
        fitsobj = maputils.FITSimage(fname)
        #print fitsobj.hdr.ascard

        # set up the matplotlib figure plot object
        fig = plt.figure(figsize=(9, 9), frameon=True)
        gspec = gridspec.GridSpec(2, 1, height_ratios=[1, 2])
        ax1 = fig.add_subplot(gspec[0])
        plt.axis('off')

        # add title
        title = """
        {object}
        Observed: {dateobs}
        Map made: {datemap}
        Rest frequency: {rest:.2f} GHz
        Observer: {person}
        """.format(object=fitsobj.hdr['OBJECT'],
                   dateobs=fitsobj.hdr['DATE-OBS'],
                   datemap=fitsobj.hdr['DATE-MAP'],
                   rest=fitsobj.hdr['RESTFREQ']/1e9,
                   person=fitsobj.hdr['OBSERVER'])
        ax1.text(0, 0, title, fontsize=12)


        # add image with coordinates (graticule)
        ax2 = fig.add_subplot(gspec[1])
        mplim = fitsobj.Annotatedimage(ax2, cmap="seismic", blankcolor='white')
        mplim.Image()
        mplim.Graticule()

        # add colorbar
        units = fitsobj.hdr['BUNIT']
        colorbar = mplim.Colorbar(fontsize=12)
        colorbar.set_label(label=units, fontsize=13)

        # plot image and save it to disk
        mplim.plot()
        basename = os.path.basename(fname)
        rootname, _ = os.path.splitext(basename)
        plt.savefig('images/{rootname}.png'.format(rootname=rootname))
        plt.close()


def create_html_summary():
    """Write an HTML file that shows all the images

    """

    # read in the template html
    html_fd = open('summary_template.html', 'r')
    rawhtml = html_fd.readlines()
    rawhtml = ''.join(rawhtml)
    template = Template(rawhtml)

    files = []
    # collect information to go into the template
    for fname in glob.glob('images/*cont.png'):
        files.append(fname)

    dirname = os.path.dirname(os.path.realpath(__file__))
    print dirname
    # render the html with info we collected
    html = template.render(dirname=dirname+'/', files=files)

    # write the rendered html
    webpage = open('image_summary.html', 'w')
    webpage.write(html)
    webpage.close()

if __name__ == '__main__':
    ARGS = get_command_line_args(sys.argv)
    create_images(ARGS.directory)
    create_html_summary()
