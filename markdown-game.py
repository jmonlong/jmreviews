import argparse
import re
import random


parser = argparse.ArgumentParser('Script to work on a markdown sections and subsections.')
parser.add_argument('-md', '--md', required=True, help='the markdown document with the glossary')
parser.add_argument('-m', '--mix', type=int, default=2,
                    help='the reinsertion factor (>=2) for the game.')

args = parser.parse_args()


class Section:
    '''A section with a title and some content.'''
    def __init__(self, filecon, current):
        self.filecon = filecon
        self.subsections = []
        self.head = ''
        self.current = current
        self.title = ''

    def readHead(self):
        sec_pat = re.compile('^# (.+)\n')
        mres = sec_pat.findall(self.current)
        if(len(mres) > 0):
            self.title = mres[0]
        subsec_pat = re.compile('^## (.+)\n')
        for line in self.filecon:
            mres = subsec_pat.findall(line)
            mres2 = sec_pat.findall(line)
            if(len(mres) > 0 or len(mres2) > 0):
                self.current = line
                break
            else:
                self.head += line
        if(len(mres) == 0 and len(mres2) == 0):
            self.filecon.close()

    def readSection(self):
        self.readHead()
        subsec_pat = re.compile('^## (.+)\n')
        mres = subsec_pat.findall(self.current)
        while(len(mres) > 0 and not self.filecon.closed):
            sec = SubSection(self.filecon, self.current)
            sec.readSection()
            self.current = sec.current
            self.subsections.append(sec)
            mres = subsec_pat.findall(self.current)


class SubSection:
    '''A subsection with a title and some content.'''
    def __init__(self, filecon, current):
        self.filecon = filecon
        self.current = current
        self.title = ''
        self.content = ''

    def readSection(self):
        sec_pat = re.compile('^# (.+)\n')
        subsec_pat = re.compile('^## (.+)\n')
        mres = subsec_pat.findall(self.current)
        if(len(mres) > 0):
            self.title = mres[0]
        for line in self.filecon:
            mres = subsec_pat.findall(line)
            mres2 = sec_pat.findall(line)
            if(len(mres) > 0 or len(mres2) > 0):
                self.current = line
                break
            else:
                self.content += line
        if(len(mres) == 0 and len(mres2) == 0):
            self.filecon.close()


class Document:
    '''A document with sections.'''
    def __init__(self, filename):
        self.sections = []
        self.filecon = open(filename, 'r')
        self.head = ''
        self.current = ''

    def readHead(self):
        sec_pat = re.compile('^# (.+)\n')
        for line in self.filecon:
            mres = sec_pat.findall(line)
            if(len(mres) > 0):
                self.current = line
                break
            else:
                self.head += line

    def readFile(self):
        self.readHead()
        while(not self.filecon.closed):
            sec = Section(self.filecon, self.current)
            sec.readSection()
            self.current = sec.current
            self.sections.append(sec)

    def playSections(self, lineskip=50, mix=2):
        index_list = random.sample(range(len(self.sections)), len(self.sections))
        total = 0
        correct = 0
        streak = 0
        while True:
            ii = index_list.pop()
            sec = self.sections[ii]
            # Give answer
            answer = raw_input(' ' + str(len(self.sections)-streak) + ' ' + sec.title + ' ?  ')
            if(answer == 'quit' or answer == 'q'):
                break
            print sec.head
            answer = raw_input(' Did you get it? ')
            if(answer == 'quit' or answer == 'q'):
                break
            if(answer == 'no' or answer == 'n'):
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
        print ' ' + str(correct) + ' / ' + str(total)

    def playSubSections(self, lineskip=50, mix=2):
        subsections = []
        for sec in self.sections:
            for subsec in sec.subsections:
                subsec.title = sec.title + ' - ' + subsec.title
                subsections.append(subsec)
        index_list = random.sample(range(len(subsections)), len(subsections))
        total = 0
        correct = 0
        streak = 0
        while True:
            ii = index_list.pop()
            sec = subsections[ii]
            # Give answer
            answer = raw_input(' ' + str(streak) + '/' + str(len(subsections)) + ' ' + sec.title + '  ')
            if(answer == 'quit' or answer == 'q'):
                break
            print sec.content
            answer = raw_input(' Did you get it? ')
            if(answer == 'quit' or answer == 'q'):
                break
            if(answer == 'no' or answer == 'n'):
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
        print ' ' + str(correct) + ' / ' + str(total)

    def play(self, lineskip=50, mix=2):
        anysubsec = False
        for sec in self.sections:
            if(len(sec.subsections) > 0):
                anysubsec = True
        if(anysubsec):
            self.playSubSections(lineskip, mix)
        else:
            self.playSections(lineskip, mix)


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
md_doc.readFile()
# print md_doc.head
# print 'Found ' + str(len(md_doc.sections)) + ' sections.'

md_doc.play(mix=args.mix)


## Next: Flask to make it interactive. Will need a way to convert markdown into HTML
