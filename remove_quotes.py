import sys
import fnmatch
import os

try:
    indir = sys.argv[1]
except:
    print "usage:", sys.argv[0], "<directory to process>"
    sys.exit()

labFiles = []
for root, dirnames, filenames in os.walk(indir):
    for filename in fnmatch.filter(filenames, '*.lab'):
        labFiles.append(os.path.join(root, filename))

for file in labFiles:
    with open(file, 'r') as content_file:
        content = content_file.read().replace('"', '')
    os.remove(file)
    file = file.replace('_vamp_nnls-chroma_chordino_simplechord','')
    with open(file, 'w') as content_file:
        content_file.write(content)
