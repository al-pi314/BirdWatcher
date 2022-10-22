// Modules for request handling
var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');

// Communication with external NN server
var request = require('request');

// Uploading of files and storage in Drive
var fileUpload = require('express-fileupload');
let {google} = require('googleapis');
let privatekey = require("./privatekey.json");
var fs = require('fs');
var archiver = require('archiver');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

// Google Drive authentication
let jwtClient = new google.auth.JWT(
    privatekey.client_email,
    null,
    privatekey.private_key,
    ['https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file']);
jwtClient.authorize(function (err, tokens) {
    if (err) {
        console.log("ERROR AUTHENTICATING!");
        return;
    } else {
        console.log("Successfully connected!");
    }
});
let drive = google.drive('v3');

// Database authentication
const Pool = require('pg').Pool
const pool = new Pool({
  user: 'burrduczxyfaei',
  host: 'ec2-54-243-238-46.compute-1.amazonaws.com',
  database: 'd5bnrfjo0lfgqb',
  password: '',
  port: 5432,
})

// Transalte form index to spicies name
var spicies = {
    "-1": 'Empty Image',
    "0": 'Carduelis carduelis',
    "1": 'Carduelis chloris',
    "2": 'Coccothraustes coccothraustes',
    "3": 'Cyanistes caeruleus',
    "4": 'Dendrocopos major',
    "5": 'Erithacus rubecula',
    "6": 'Fringilla coelebs',
    "7": 'Fringilla montifringilla',
    "8": 'Parus major',
    "9": 'Parus palustris',
    "10": 'Passer domesticus',
    "11": 'Passer montanus',
    "12": 'Peri ater',
    "13": 'Pyrrhula pyrrhula',
    "14": 'Sitta europaea'
}

// Setup of express app
var app = express()
app.use(express.json({limit:'50mb'}))
app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(fileUpload())
app.set('port', (process.env.PORT || 5000))
app.use(express.static(__dirname + '/public'))
app.set('views', path.join(__dirname, '/views'));
app.use(cookieParser());


function getDriveFile(index, drive_ids , dir, zip_dir, res) {
    var drive_id = drive_ids[index]
    var copy_dest = dir + "/" + drive_id + ".jpeg";
    var file_stream = fs.createWriteStream(copy_dest)
    drive.files.get({
        auth: jwtClient,
        fileId: drive_id,
        alt: 'media',
        fields: "kind,items(title),data"
    }, {responseType: 'stream'}, function(err, response) {
        response.data
        .on('end', () => {
            index += 1
            console.log("Index: " + index + "File with id " + drive_id + " ready for download!")
            if (index >= drive_ids.length) {
                console.log("All files ready for download ... Zipping folder ...")
                var output = fs.createWriteStream(zip_dir);
                output.on('close', function() {
                    console.log(archive.pointer() + ' total bytes');
                    console.log('It is now safe to download!');
                    console.log("Downloading...")
                    res.setHeader('Content-Disposition', 'attachment');
                    res.download(zip_dir)
                  });

                var archive = archiver('zip', { zlib: { level: 9 } });
                archive.pipe(output);

                archive.directory(dir, ".thumbimage");
                console.log("Finalizing...")
                archive.finalize();
            } else {
                getDriveFile(index, drive_ids, dir, zip_dir, res)
            }
        })
        .on('error', (err) => {
            console.log("ERROR storing files for folder download!: ", err)
        })
        .pipe(file_stream);
    })
}

var deleteFolderRecursive = function(path) {
    if (fs.existsSync(path)) {
      fs.readdirSync(path).forEach(function(file, index){
        var curPath = path + "/" + file;
        if (fs.lstatSync(curPath).isDirectory()) { // recurse
          deleteFolderRecursive(curPath);
        } else { // delete file
          fs.unlinkSync(curPath);
        }
      });
      fs.rmdirSync(path);
    }
  };

// Main page
app.get("/", (req, res) => {
    res.render("index.ejs")
});

app.get("/test", (req, res) => {
    pool.connect((err, client, done) => {
        if (err) throw err;
        client.query("SELECT id, human_label, nn_label, temp, pres, hum, date FROM image_data ORDER BY id;", 
        [], (err, db_res) => {
            done();
            if (err) {
                console.log(err.stack)
            } else {
                console.log("Querry Done")
                const csvWriter = createCsvWriter({
                    path: 'sample.csv',
                    header: [
                        {id: 'id', title: 'Image ID'},
                        {id: 'human_label', title: 'Human Label'},
                        {id: 'nn_label', title: 'NN Label'},
                        {id: 'temp', title: 'Temperature'},
                        {id: 'pres', title: 'Pressure'},
                        {id: 'hum', title: 'Humidity'},
                        {id: 'date', title: 'date'},
                    ]
                });
                console.log("Writing to CSV...")
                csvWriter.writeRecords(db_res.rows)
                    .then(() => {
                        console.log('...Done');
                        res.download('sample.csv')
                });
            }
        });
    });
})

// View links to images
app.get("/images", (req, res) => {
    var search_params = {
        auth: jwtClient,
        q: "name contains 'NNimage'",
        pageSize: 10,
    }

    var dont_set = false;
    if (req.cookies.nextPageToken !== undefined && req.cookies.nextPageToken != 'undefined' && req.cookies.requestNextPage == 'yes') {
        search_params['pageToken'] = req.cookies.nextPageToken;
        console.log("Next page of images listing requested!")
    } else if (req.cookies.thisPageToken !== undefined && req.cookies.thiPageToken != 'undefined') {
        search_params['pageToken'] = req.cookies.thisPageToken;
        dont_set = true;
        console.log("Refresh of images listing requested!")
    } else {
        console.log("Back to the begining of images listing requested!")
    }

    drive.files.list(search_params, 
        function(err, response) {
            if (err) {
                console.log("Error listing all the files: ");
                res.clearCookie('nextPageToken');
                res.clearCookie('thisPageToken');
                res.clearCookie('requestNextPage');
                console.log("-> Forced to refresh page without cookies!")
                res.redirect("/images");
            } else {
                console.log("Retrived files from drive.")
                console.log(response.data.files)

                if (typeof response.data.nextPageToken !== undefined) {
                    var nextPageToken = response.data.nextPageToken
                    if (!dont_set) {
                        var thisPageToken = req.cookies['nextPageToken']
                        res.cookie('thisPageToken' , thisPageToken);
                    }
                    res.cookie('nextPageToken' , nextPageToken);
                } else {
                    res.clearCookie('nextPageToken');
                    var thisPageToken = req.cookies['nextPageToken']
                    res.cookie('thisPageToken' , thisPageToken);
                }

                res.render("images.ejs", {files: response.data.files})
            }
        }
    );
})

app.get("/images/download", (req, res) => {
    res.render("download.ejs")
})

app.post("/images/download", (req, res) => {
    if (req.body.password == "") {
        var limit = req.body.limit;
        var spicies_name = spicies[req.body.spicies_id]

        // Assure that download folder is empty and ready for use
        var dir = './download_files/' + spicies_name
        var zip_dir = './download_files/zipped/' + spicies_name + ".zip"
        if (fs.existsSync(dir)){
            deleteFolderRecursive(dir)
        }
        fs.mkdirSync(dir);

        pool.connect((err, client, done) => {
            if (err) throw err;
            client.query("SELECT drive_id FROM image_data WHERE human_label = $1 ORDER  BY id DESC LIMIT $2;", 
            [spicies_name, limit], (err, db_res) => {
                done();
                if (err) {
                    console.log(err.stack)
                } else {
                    console.log("Prepering images for download, NO. of images: ", Object.keys(db_res.rows).length)
                    if (Object.keys(db_res.rows).length != 0) {
                        var drive_ids = []
                        for(let row of db_res.rows) {
                            drive_ids.push(row.drive_id)
                        }
                        getDriveFile(0, drive_ids, dir, zip_dir, res)
                    } else {
                        res.redirect("/images/download?r=0")
                    }
                }
            })
        })
    } else {
        res.redirect("/images/download?r=f")
    }
})

// View a single image
app.get("/images/view", (req, res) => {
    var file_id = req.query.id
    var destination = fs.createWriteStream('/app/public/temp-images/photo.jpeg');
    drive.files.get({
        auth: jwtClient,
        fileId: file_id,
        alt: 'media',
        fields: "kind,items(title),data"
    }, {responseType: 'stream'}, function(err, response) {
        response.data
        .on('end', () => {
            console.log("Retrived file " + file_id)
            if (fs.existsSync("/app/public/temp-images/photo.jpeg")) {
                console.log("File Exists and is ready for display!")
            }
            pool.connect((err, client, done) => {
                if (err) throw err;
                client.query("SELECT * FROM image_data WHERE drive_id=$1", 
                [file_id], (err, db_res) => {
                    done();
                    if (err) {
                        console.log(err.stack)
                    } else {
                        var row = db_res.rows[0]
                        res.render("view_image.ejs", row)
                    }
                })
            })
        })
        .on('error', (err) => {
            console.log("ERROR druing download: ", err)
        })
        .pipe(destination);
    })
})

// Updating human set label on an image
app.post("/images/view", (req, res) => {
    var file_id = req.body.file_id
    if (req.body.password === "") {
        var spicies_index = req.body.spicies;
        var spicies_name = spicies[spicies_index];
        console.log("Manual setting of bird spicies label: ")
        console.log(file_id)
        console.log(spicies_name)
        console.log("Password is correct!")

        pool.connect((err, client, done) => {
            if (err) throw err;
            client.query("UPDATE image_data SET human_label = $1 WHERE drive_id = $2 RETURNING id",
             [spicies_name, file_id], (err, db_res) => {
                done()

                if (err) {
                  console.log(err.stack)
                } else {
                  for(let row of db_res.rows) {
                      console.log("Updates spicies at id: " + row.id)
                  }
                  res.redirect("/images/view?id=" + file_id + '&' + 'r=s');
                };
            });
        });
    } else {
        res.redirect("/images/view?id=" + file_id + '&' + 'r=f');
    }
});


// Retrival of images and data from Bird Feeder
app.post("/data", (req, res) => {
    if (!req.files) {
        console.log('No file recieved!')
        return res.status(400).send('No file recieved!')
    } else {
        var date = new Date()
        var current_hours = date.getHours() +1
        if (current_hours <= 18 && current_hours >= 7) {
            // Image data
            let image = req.files.media
            let image_name = req.body.image_name
            var image_location = __dirname + '/public/temp-images/upload/' + image_name
            console.log("Recived image with name: " + image_name)

            // Aditional data
            var temp = req.body.temp
            var pres = req.body.pres
            var hum = req.body.hum

            // Move image to NN evaluation folder
            image.mv(image_location, function(err) {
                if (err) {
                    console.log(err)
                    return res.status(500).send(err)
                }
                console.log("Image saved to a temporary folder for NN.")

                // Set main information about the file we will create 
                var fileMetadata = {
                    'name': "NNimage_" + image_name,
                };
                var media = {
                    mimeType: 'image/jpeg',
                    body: fs.createReadStream(image_location)
                };
                
                // Save image to Drive
                drive.files.create({
                    auth: jwtClient,
                    resource: fileMetadata,
                    media: media,
                }, function (err, file) {
                    if (err) {
                        console.log('Error on Drive Upload!')
                        console.error(err);
                    } else {
                        var drive_id = file.data.id
                        console.log('Image saved with Id: ', drive_id);

                        // NEURAL NETWORK
                        const formData = {
                            password: '',
                            image:  fs.createReadStream(image_location)
                        };
                        request.post({url:'http://bn-nn-server.herokuapp.com/', formData: formData}, function optionalCallback(err, httpResponse, body) {
                            if (err) {
                            return console.error('upload failed:', err);
                            }
                            var prediction = JSON.parse(body).predictions[0]
                            var spicies_name = spicies[prediction]
                            console.log("Second Server predicted: " + spicies_name) // NN Prediction

                            // Save data to database
                            var current_date = new Date(Date.now()).toString().split(" (")[0]
                            pool.connect((err, client, done) => {
                                if (err) throw err;
                                client.query('INSERT INTO image_data (drive_id, nn_label, temp, hum, pres, date) VALUES($1, $2, $3, $4, $5, $6) RETURNING id;', 
                                [drive_id, spicies_name, temp, hum, pres, current_date], (err, db_res) => {
                                    done()

                                    if (err) {
                                    console.log(err.stack)
                                    } else {
                                    for(let row of db_res.rows) {
                                        console.log("Image saved in database under id: " + row.id)
                                    }
                                    res.send('Everything OK - (Image stored, Data saved to Database, Image awaitng evaluation).')
                                    }
                                })
                            })
                        });
                    }
                });

            })
        } else {
            res.send('Rejected!')
        }
    }
})

app.listen(app.get('port'), function() {
  console.log("Node app is running at localhost:" + app.get('port'))
})