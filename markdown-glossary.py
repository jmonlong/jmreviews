import argparse
import re
import random


parser = argparse.ArgumentParser('Script to work on a glossary.')
parser.add_argument('-md', '--md', required=True, help='the markdown document with the glossary')
parser.add_argument('-order', '--order', action='store_true',
                    help='Order the sections')
parser.add_argument('-out', '--out', default='out.md', help='the output file')
parser.add_argument('-play', '--play', action='store_true',
                    help='Play ! Yeay !')
parser.add_argument('-m', '--mix', type=int, default=2,
                    help='the reinsertion factor (>=2) for the game.')
parser.add_argument('-sec', '--sec', type=int, default=2,
                    help='the section level.')

args = parser.parse_args()


class Section:
    '''A section with a title and some content.'''
    def __init__(self, filecon):
        self.filecon = filecon
        self.last = ''
        self.title = ''
        self.content = ''

    def readSection(self, current, seclvl=2):
        sec_pat = re.compile('^' + '#' * seclvl + ' (.+)\n')
        mres = sec_pat.findall(current)
        if(len(mres)>0):
            self.title = mres[0]
        for line in self.filecon:
            mres = sec_pat.findall(line)
            if(len(mres) > 0):
                self.last = line
                break
            else:
                self.content += line
        if(len(sec_pat.findall(self.last)) == 0):
            self.filecon.close()


class Document:
    '''A document with sections.'''
    def __init__(self, filename):
        self.sections = []
        self.filecon = open(filename, 'r')
        self.head = ''
        self.current = ''

    def readHead(self, seclvl=2):
        sec_pat = re.compile('^' + '#' * seclvl + ' (.+)\n')
        for line in self.filecon:
            mres = sec_pat.findall(line)
            if(len(mres) > 0):
                self.current = line
                break
            else:
                self.head += line

    def readFile(self, seclvl=2):
        self.readHead(seclvl=seclvl)
        while(not self.filecon.closed):
            sec = Section(self.filecon)
            sec.readSection(self.current, seclvl=seclvl)
            self.current = sec.last
            self.sections.append(sec)

    def reorder(self):
        self.sections = sorted(self.sections, key=lambda k: k.title.lower())

    def drawOne(self):
        sec = self.sections[int(random.random() * len(self.sections))]
        answer = raw_input(sec.title + ' ?')
        print sec.content
        answer = raw_input('Did you get it ? ')
        if(answer == 'no' or answer == 'n'):
            print 'Looooser !'
        else:
            print 'Lucky guess...'

    def play(self, lineskip=50, mix=2):
        index_list = random.sample(range(len(self.sections)), len(self.sections))
        total = 0
        correct = 0
        streak = 0
        while True:
            ii = index_list.pop()
            sec = self.sections[ii]
            # Give answer
            answer = raw_input(str(len(self.sections)-streak) + ' ' + sec.title + ' ?  ')
            if(answer == 'quit'):
                break
            print sec.content
            answer = raw_input('Did you get it? ')
            if(answer == 'quit'):
                break
            if(answer == 'no' or answer == 'n' or answer == ''):
                index_list.insert(int(float(len(index_list)/mix) +
                                      random.random()*float(len(index_list)/mix)), ii)
                streak = 0
                print 'Looooser!'
            else:
                index_list.insert(0, ii)
                correct += 1
                streak += 1
                print 'Good job!'
            total += 1
            print '\n' * lineskip
        # Exit message
        print str(correct) + ' / ' + str(total)

    def writeFile(self, filename, seclvl=2):
        outfile = open(filename, 'w')
        outfile.write(self.head)
        for sec in self.sections:
            print sec.title
            outfile.write('#' * seclvl + ' ' + sec.title + '\n' + sec.content)


## Reading a MD document
# test = Document('test.md')
# test.readFile()
# test.head
# len(test.sections)
# sec = test.sections[0]
# sec.content

# ## Reordering sections
# test.sections[0].title
# test.reorder()
# test.sections[0].title
# test.writeFile('testOrdered.md')

# ## Showing a random title and content
# test.drawOne()
# test.play()

md_doc = Document(args.md)
md_doc.readFile(seclvl=args.sec)
# print md_doc.head
# print 'Found ' + str(len(md_doc.sections)) + ' sections.'

if(args.order):
    md_doc.reorder()
    md_doc.writeFile(args.out, seclvl=args.sec)

if(args.play):
    md_doc.play(mix=args.mix)


## Next: Flask to make it interactive. Will need a way to convert markdown into HTML
