mdfiles := content/fixed/*.Rmd content/post/*.Rmd

serve: library-small.bib
	Rscript -e 'blogdown::serve_site()'

build: docs/index.html

docs/index.html: $(mdfiles) library-small.bib
	Rscript -e 'blogdown::build_site()'

library-small.bib: $(mdfiles) library.bib
	python3 reduceBib.py -b library.bib -o library-small.bib $(mdfiles)

epub: jmreviews-ebook.epub

jmreviews-ebook.epub: docs/index.html
	echo -e " <dc:title>My Reviews</dc:title>\n<dc:author>Jean Monlong</dc:author>\n" > title.txt
	pandoc -f html-native_divs  -o jmreviews-ebook.epub --epub-metadata title.txt docs/SVs-biology/index.html docs/SVs-methods/index.html docs/SVs-mechanisms/index.html docs/SVs-impact/index.html docs/SVs-repeats/index.html docs/WGS-misc/index.html docs/VG-brainstorm/index.html docs/glossary/index.html docs/phdquestions/index.html docs/expression/index.html
	rm title.txt

clean:
	rm -f library-small.bib jmreviews-ebook.epub title.txt
