#!/usr/bin/env bash
var path = require("path");

var currentPath = path.resolve(".");

var fs = require('fs'),
    fileList = [];

function walk(filepath){
    var dirList = fs.readdirSync(filepath);
    dirList.forEach(function(item){
        if(fs.statSync(filepath + '/' + item).isDirectory()){
            walk(filepath + '/' + item);
        }else{
            fileList.push(filepath + '/' + item);
            fs.mkdir(path.join(__dirname, '../../../../../console-fe/privateCloud/console/js/admin'), function(err){
                // if(err) console.log(err);
            })
            transtoReact(item, filepath + '/' + item, path.join(__dirname, '../../../../../console-fe/privateCloud/console/js/admin'));
        }
    });
}

function transtoReact(item, path, newPath) {
    fs.open(path, 'r', function (err, fd) {
        fs.readFile(fd, 'utf8', function(err, data){
            var commonHeaderReactWrapper = 'module.exports = React.createClass({\nrender: function() {\nreturn (<div>';
            var commonFooterReactWrapper = '</div>)\n}\n});';
            var result = data.replace(/\{\%\D+\%\}/g, "");
            result = result.replace(/\$\{\D+\}/g, "");
            result = result.replace(/\n<!DOCTYPE html>\n<html lang="zh-CN">/g, "");
            result = result.replace(/(\<head\>)([\s\S]*)(\<\/head\>)/g,"");
            result = result.replace(/<\/body>/g, "");
            result = result.replace(/<\/html>/g, "");
            result = result.replace(/class="/g, "className=\"");
            // console.log(data);
            data = commonHeaderReactWrapper + result + commonFooterReactWrapper;
            fs.writeFile((newPath + "/" + item).replace("html", "jsx"), data, function(err){
                // console.log('写数据总数：'+readByte+' bytes' );
                // ==>写数据总数：27 bytes
            })
        })



    })
}

walk('.');

// console.log(fileList);