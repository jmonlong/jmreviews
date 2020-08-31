import argparse
import re
# import glob

parser = argparse.ArgumentParser(description='Reduce a .bib file.')
parser.add_argument('-b', dest='bib', default="static/library.bib",
                    help='the original bib file')
parser.add_argument('-o', dest='out', default="static/library-small.bib",
                    help='the new bib file')
parser.add_argument('-a', dest='nauths', type=int, default=5,
                    help='the maximum number of authors. Default: 5.')
parser.add_argument('-f', dest='fields',
                    default='author,title,doi,journal,year,url',
                    help='the BibTeX fields to keep (comma separated). '
                    'Default: "author,title,doi,journal,year,url"')
parser.add_argument('mds', nargs='+',
                    help='the markdown files to scan')

args = parser.parse_args()
keepinfo = args.fields.split(',') + ['jmreviews']
tagre = re.compile(' *([a-z]+).*=.*')
citere = re.compile('.*{([^,]+),')

print "Original bib file: \t" + args.bib
print "Output file: \t" + args.out
print "BibTeX fields: \t" + args.fields
print "Max # authors: \t" + str(args.nauths)


class Citation:
    '''A citation.'''
    def __init__(self, line):
        line = line.strip()
        m = citere.match(line)
        self.ref = m.group(1)
        self.info = [line]
        self.tagidx = {}

    def addInfo(self, line):
        line = line.rstrip(",")
        m = tagre.match(line)
        if(m is None):
            return(False)
        if(m.group(1) in keepinfo):
            self.tagidx[m.group(1)] = len(self.info)
            self.info.append(line)

    def shortenAuthors(self, nb_auth_max=5):
        if 'author' in self.tagidx:
            auth_idx = self.tagidx['author']
            auths = self.info[auth_idx]
            auths = auths.split(' and ')
            if len(auths) > nb_auth_max:
                auths = auths[:(nb_auth_max-1)] + ['...'] + [auths[-1]]
                self.info[auth_idx] = ' and '.join(auths)

    def write(self, fileCon):
        for ii in range(len(self.info)-1):
            line = self.info[ii]
            line = line.strip()
            line = line.rstrip("\n")
            line = line.rstrip(',')
            fileCon.write(line)
            fileCon.write(",\n")
        line = self.info[len(self.info)-1]
        line = line.strip()
        line = line.rstrip("\n")
        line = line.rstrip(',')
        fileCon.write(line)
        fileCon.write("\n}\n")


class CitationList:
    '''A list of citations.'''
    def __init__(self):
        self.cits = []

    def parseCit(self, line, fileCon):
        while(line.find('@') == -1):
            line = fileCon.next()
        cit = Citation(line)
        for line in fileCon:
            if(line.find('@') == 0):
                cit.shortenAuthors(nb_auth_max=args.nauths)
                self.cits.append(cit)
                return line
            cit.addInfo(line)
        cit.shortenAuthors(nb_auth_max=args.nauths)
        self.cits.append(cit)
        return False

    def parseBib(self, filename):
        ffile = open(filename)
        line = self.parseCit(ffile.next(), ffile)
        while(line):
            line = self.parseCit(line, ffile)
        ffile.close()

    def writeCitations(self, outBib, citToWrite):
        # Print missing refs
        cits = [cit.ref for cit in self.cits]
        for cit in citToWrite:
            if cit not in cits:
                print 'Missing ref: ' + cit
        outCon = open(outBib, 'w')
        for cit in self.cits:
            if cit.ref in citToWrite:
                # new info about page citing it
                cit.addInfo('jmreviews={'+','.join(citToWrite[cit.ref])+'}')
                # write citation
                cit.write(outCon)
        outCon.close()


# transform a title into URL form
def titleToUrl(title):
    # transform special characters to spaces
    for cc in ['(', ')', ',', '-', '\'', '"']:
        title = title.replace(cc, ' ')
    # lowercase and remove trailing spaces
    title = title.lstrip().rstrip().lower()
    # replace white spaces by one -
    title = re.sub(r" +", '-', title)
    return title


# find the corresponding URL of a Rmd page
def findUrl(rmd_file):
    # read yaml header
    info = {}
    with open(rmd_file, 'r') as inf:
        cpt = 0
        for line in inf:
            if '---' in line:
                cpt += 1
            if cpt == 2:
                break
            line = line.rstrip().split(':')
            if len(line) > 1:
                info[line[0]] = ':'.join(line[1:])
    # if fixed/page, use title. Otherwise use slug or dates.
    if 'content/fixed' in rmd_file:
        return titleToUrl(info['title'])
    else:
        if 'date' in info:
            pdate = info['date'].split('-')
        else:
            pdate = rmd_file.split('-')[:3]
        if 'slug' in info:
            ptitle = info['slug']
        else:
            ptitle = titleToUrl(info['title'])
        return '{}/{}'.format('/'.join(pdate), ptitle)
    return rmd_file


# Read bibtex file
bl = CitationList()
bl.parseBib(args.bib)

# Read all md files and find references
mdre = re.compile('@([a-zA-Z0-9\-]+)')
cits = {}
for ff in args.mds:
    ff_url = findUrl(ff)
    ffile = open(ff)
    for line in ffile:
        citline = mdre.findall(line)
        citlineU = []
        for tt in citline:
            citlineU.extend(tt.split())
        if(len(citlineU) > 0):
            for cl in citlineU:
                if(cl not in cits):
                    cits[cl] = [ff_url]
                else:
                    if ff_url not in cits[cl]:
                        cits[cl].append(ff_url)

# Write output bibbtex
bl.writeCitations(args.out, cits)
