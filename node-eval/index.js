const fs = require('fs');

const FROM = "../korp-frontend-sb/app/";

const PATH = "source/";
const MODES = PATH + "modes";

function copy() {
  // this function will copy files from
}

// before it's possible to eval files using node, we must remove
// some specific lines
function preprocess() {
  // process common.js
  // remove all lines matching catToString
  fs.readFile(`${MODES}/common.js`, 'utf8', function (err,data) {
    if (err) {
      return console.log(err);
    }

    const result = data.split('/n').filter((line) => {
      return !line.contains('catToString');
    }).join('/n');

    fs.writeFile(`${MODES}/common.js`, result, 'utf8', function (err) {
       if (err) return console.log(err);
    });
  });

  // for each mode remove calls to CorpusListing
  fs.readdirSync(MODES).forEach(file => {
    if (file.endsWith('_mode.js') && file != 'npegl_mode.js') {

    }
  });
}

function readAllModes() {
  global['_'] = require('lodash');

  global['window'] = {};
  global['settings'] = {};
  global['isLab'] = false; //TODO also need to handle the isLab cases

  require(`${PATH}config.js`);
  let commonSettings = require(`${MODES}/common.js`);

  _.map(commonSettings, function(v, k) {
    if (k in global) {
      console.error("warning, overwriting setting" + k)
    }
    global[k] = v
  })

  const modes = {};

  fs.readdirSync(MODES).forEach(file => {
    if(file.endsWith('_mode.js') && file != 'npegl_mode.js') {
      global['settings'] = {}
      require(`../korp-frontend-sb/app/modes/${file}`);
      modes[file.split('_mode.js')[0]] = global['settings'];
    }
  });
  return modes;
}

function writeNewModes(modes) {
  for(let mode in modes) {
    const modeObj = modes[mode];
    modeObj.pop("attributes");
    modeObj.pop("structAttributes");
    let content = JSON.stringify(modeObj, null, 4);
    content = 'export default ' + content;
    fs.writeFile(`/home/maria/språkbanken/korp/korp-frontend-sb/app/modes/${mode}_mode.js`, content, function(err) {
      if(err) {
        console.log('err writing', err);
      }
    });
  }
}

function writeSettingsToFile(modes) {
  for(let mode in modes) {
    let content = JSON.stringify(modes[mode], null, 4);
    fs.writeFile(`modes/${mode}.json`, content, function(err) {
      if(err) {
        console.log('err writing', err);
      }
    });
  }
}

// make files evaluable
preprocess();

//const modes = readAllModes();
//for(let mode in modes) {
  //modes[mode]['corpora'] = undefined;
//}


// does not change mode
//writeSettingsToFile(modes);
// changes mode
//writeNewModes(modes);
