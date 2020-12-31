from flask import Flask,render_template,request, abort, jsonify
from flask_restful import Resource, Api
import os
app = Flask(__name__)
api = Api(app)

#Basic Web app for home page to upload
@app.route('/')
def home():
    return render_template("index.html")


#Api endpoint recieving the upload!! 
class api_end_point(Resource):
    def get(self):
        resumableIdentfier = request.args.get('resumableIdentifier', type=str)
        resumableFilename = request.args.get('resumableFilename', type=str)
        resumableChunkNumber = request.args.get('resumableChunkNumber', type=int)

        if not resumableIdentfier or not resumableFilename or not resumableChunkNumber:
            abort(500, 'Parameter error')

        temp_dir = os.path.join(temp_base, resumableIdentfier)


        chunk_file = os.path.join(temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))
        

        if os.path.isfile(chunk_file):
            return('OK')
        else:
            abort(404, 'Not found')
    
    def post(self):
        resumableTotalChunks = request.form.get('resumableTotalChunks', type=int)
        resumableChunkNumber = request.form.get('resumableChunkNumber', default=1, type=int)
        resumableFilename = request.form.get('resumableFilename', default='error', type=str)
        resumableIdentfier = request.form.get('resumableIdentifier', default='error', type=str)

        chunk_data = request.files['file']

        temp_dir = os.path.join(temp_base, resumableIdentfier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir, 0o777)


        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(temp_dir, chunk_name)
        chunk_data.save(chunk_file)
        

        chunk_paths = [os.path.join(temp_dir, get_chunk_name(resumableFilename, x)) for x in range(1, resumableTotalChunks+1)]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        if upload_complete:
            target_file_name = os.path.join(temp_base, resumableFilename)
            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    stored_chunk_file_name = p
                    stored_chunk_file = open(stored_chunk_file_name, 'rb')
                    target_file.write(stored_chunk_file.read())
                    stored_chunk_file.close()
                    os.unlink(stored_chunk_file_name)
            target_file.close()
            os.rmdir(temp_dir)
            

        return 'OK'

api.add_resource(api_end_point, '/u')


temp_base = os.path.expanduser("~/tmp/flask_uploads/")




def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_%03d" % chunk_number


if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 5001)