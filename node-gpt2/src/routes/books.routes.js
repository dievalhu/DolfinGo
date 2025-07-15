const router = require("express").Router();
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');
///End Sockets


///Variables
let titlesearchindex = ""
    //////////////////////////////////Routes Para buscar desde Index
router.post("/", async(req, res) => {

    const { nameSearch } = req.body;
    let word = nameSearch;
    titlesearchindex = word
    var enc = word.replace(/[.*+?^${}()|[\]\\:;.\-\>\<]/g, "")
    var url_abst = encodeURI(enc)
 
    const respuesta = await axios.get(`http://docker-flaskapirest:4000/api/search/documents/${url_abst}`);
    req.session.data = respuesta.data


    res.redirect('books/1');

});

router.get('/books/:page', (req, res, next) => {

    //const dataJson = require("../data/data.json")
    let data = req.session.data;


    let perPage = 5;
    let page = req.params.page || 1;
    const jsd = data.slice((perPage * page) - perPage, ((perPage * page) - perPage) + perPage) // in the first page the value of the skip is 0
    console.log(jsd)
    
    res.render('books/all-books', {
        jsd,
        current: page,
        pages: Math.ceil(data.length / perPage),
        titlesearchindex
    });


});


//////////////////////////////////End Para buscar desde Index

//////////////////////////////////////Routes Para buscar por Similitud

router.post("/ajax", async(req, res) => {
    const { id } = req.body;
    let word2 = id;
    var enc = word2.replace(/[.*+?^${}()|[\]\\:;.\-\>\<]/g, "")
    var url_abst = encodeURI(enc)


    const respuesta = await axios.get(`http://docker-flaskapirest:4000/api/search/Similarydocuments/${url_abst}`);
    req.session.data1 = respuesta.data

    res.redirect('/booksPro')

});


router.get('/booksPro', (req, res) => {
    let data = req.session.data1;
    res.json(data)
});


//////////////////////////////////////END Routes Para buscar por Similitud




//////////////////////////////////////START ROUTES GTP2
router.post('/gptView', async(req, res) => {
    const { titlegpt2, abstractgpt2 } = req.body;
    let sendtitle = titlegpt2
    let sendabstract = abstractgpt2
    var enc = sendtitle.replace(/[.*+?^${}()|[\]\\:;.\-\>\<\/]/g, "")
    var url_abst = encodeURI(enc)


    var enc2 = sendabstract.replace(/[.*+?^${}()|[\]\\:;.\-\>\<\/]/g, "")
    var url_abst2 = encodeURI(enc2)

    const respuesta = await axios.get(`http://docker-flaskapirest:4000/api/search/GPT2/${url_abst}/${url_abst2}`);
    req.session.data2 = respuesta.data
    let data = req.session.data2;
    res.render('books/gpt2-books', {
        data,
        sendabstract,
        sendtitle
    });

});


//////////////////////////////////////END ROUTES GTP2

////////////////////////////////////// Contact 

router.post('/contact-save', (req, res) => {
    const { name, email, subject, msg } = req.body;
    console.log(req.body);
    res.redirect('/');
});

module.exports = router;
