from flask import send_from_directory,Flask, request, session, g, redirect, url_for, abort,render_template
from werkzeug import secure_filename
from elasticsearch import Elasticsearch,helpers
from elasticsearch_dsl import Search, Q
from urllib.request import urlopen
import nltk,re,json,os
from scriptindex import text_blocks

es = Elasticsearch()

# mapping for elastic search's document
mapping = {"book": 
				 {"properties":
				 {"_id":
				 {"type": "string", "index": "not_analyzed"},  
					"text": {"type": "string", "analyzer": "snowball"}}}}

ans = []
UPLOAD_FOLDER = None
ALLOWED_EXTENSIONS = ['txt']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		fil = request.files['file']
		UPLOAD_FOLDER = request.form['folder']
		url = request.form['url']
		if fil and allowed_file(fil.filename):
			filename = secure_filename(fil.filename)
			esname = filename.lower()
			fil.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			#es.indices.delete(index=esname)
			es.indices.create(esname)
			es.indices.put_mapping(index=esname, doc_type="books", body=mapping)
			text_group = text_blocks()
			count = 0
			for i in text_group:
				count+=1
				es.index(index=esname,doc_type='books',id = count,body=i)

			return redirect(url_for('uploaded_file',filename=filename))
	return render_template("upload.html")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	with open(UPLOAD_FOLDER+filename, "r") as f:
		global x
		x = filename.lower()
		print(x)
		content = f.read()
	return render_template("viewres.html", content=content)
	

@app.route('/viewall')
def view_allfile():
	allfiles = [f for f in os.listdir(UPLOAD_FOLDER)]
	return render_template('viewal.html', allfiles=allfiles)


@app.route('/search', methods = ['POST'])
def search():
	q = request.form['query']
	query = {
		"query": {
		"match": {
		"text": {
		"query": q ,
		"analyzer":"snowball",
		"operator":"and",
		"fuzziness":3,
		"slop":20}}},
		"highlight": { "fields": { "text": {} }}}
	result = es.search(index=x,body = query)
	for i in result['hits']['hits']:
		ans.append(i['_source']['text'])

	return redirect('/searchresult.html')


@app.route('/searchresult.html')
def results():
	return render_template('searchresult.html', ans=ans)


if __name__ == '__main__':
	app.run(debug=True)