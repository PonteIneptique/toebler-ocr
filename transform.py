import click
import bs4
import more_itertools

SEP_1 = "|-- "
SEP_2 = "|---- "
STYLE = """
			body {
	background: #f3f3f3;
	
	
	
}

[contenteditable=true]:empty:before {
	content: attr(data-placeholder);
	display: block; /* For Firefox */
}

li[contenteditable=true]:hover, li[contenteditable=true].hovered, span[contenteditable=true]:hover, span[contenteditable=true].hovered {
	border: 1px solid #ff0000;
}

.rect:hover, a.hovered {
	box-shadow: inset 0 0 0 1px #ff0000;
}

li[contenteditable=true]{
	border: 1px dashed #000;
	width: 100%;
	padding: 2px;
	margin: 0 0 2px 0;
}

ul {
	list-style-type:none;
}

nav {
	background: #444;
	position: fixed;
	top: 0;
	left: 0;
	height: 100%;
	width: 5%;
	font-family: "Helvetica Neue", Arial, sans-serif;
}

nav ul {
	list-style: none;
	margin-right: 1em;
}

nav li {
	display : inline-block;
}

nav a {
	color: white;
	text-decoration: none;
}

nav a:hover {
	text-decoration: underline;	
}

.container {
	position: relative;
	margin-left: 8%;
	display: table;
	height: 100%;
	width: 92%;
}

.img_container {
	position: relative;
}

.column {
	display: table-cell;
	vertical-align: top;
	height: 100%;
	padding: 5px;
	width: 25%;
	font-size:0.8em;
}

.column:first-of-type {
	width: 50%;
}

#download_button {
	position: fixed;
	padding: 0;
	text-align: center;
	width: 5%;
	bottom: 50px;
}
ul { margin:0; padding:0; }
.corrected {
	background-color: #73AD21;
}

@media all and (max-width: 1024px) {
  .column { width:0%; }
  .column:first-of-type { display:none; }
}"""


@click.command()
@click.argument("files", nargs=-1, type=click.File('r'))
@click.option("-c", "--columns", type=int, default=2, help="Number of column in pages")
def transform(files, columns=2):
    for file in files:
        print("File %s " % file.name)
        source_html = bs4.BeautifulSoup(file.read(), features="html.parser")
        for ind_page, page in enumerate(source_html.select(".page")):
            print(SEP_1+"Reading page %s " % ind_page)
            for ind_col, col in enumerate(page.select(".column")):
                if ind_col == 0:
                    last_col = [col]
                else:
                    lines = col.select("li")
                    print(SEP_2+"Number of lines %s " % len(lines))
                    lines_per_column = len(lines) // 2
                    print(SEP_2+"Number of lines per column: %s" % lines_per_column)
                    for ind_grp, group in enumerate(more_itertools.divide(columns, lines)):
                        # Create new tags
                        new_col = source_html.new_tag("div", attrs={"class": "column"})
                        new_ul = source_html.new_tag("ul")
                        # Insert new tags
                        for line in group:
                            new_ul.append(line)
                        new_col.append(new_ul)
                        last_col[-1].insert_after(new_col)
                        # Register last column
                        last_col.append(new_col)
                    # Remove original column
                    del col
            print(file.name.replace(".html", ".modified.html"))
            style = source_html.find("style")
            style.string = STYLE
            with open(file.name.replace(".html", ".modified.html"), "w") as f:
                f.write(str(source_html))


if __name__ == "__main__":
    transform()
