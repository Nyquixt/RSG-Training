'use strict'
const {Controller} = require('@sabaki/gtp')
const helpers = require('./helpers')
const fs = require('fs');

/*
    example: node selfplay.js -e ./engine/leelaz -w ./networks/8.5-network.txt -v 50 -m 10 --randomtemp 1 -r 0 -b 7 -k 8.5 --numgame 10 --sgfname ./sgf/sgf1
    args: [
        weight,
        visit,
        randomMove,
        randomTemp,
        resignRate,
        boardSize,
        komi,
        numGame,
        sgfFolder,
        sgf
    ]
*/

// yargs to better manage the flags
var argv = require('yargs/yargs')(process.argv.slice(2)).argv

let engineFile = argv.e
let weightFile = argv.w
let visit = argv.v
let randommove = argv.m
let randomtemp = argv.randomtemp
let resignrate = argv.r
let boardsize = argv.b
let komi = argv.k
let numGame = argv.numgame
let sgfName = argv.sgfname

async function selfplay() {
    const file = engineFile;
    // arguments for full strength play
    // const args = [ "-g", "-q", "--noponder", "-w", "./networks/8.5-network.txt", "-p", "50", "-r", "0", "--gpu", "0", "--seed", "942657784235445" ];

    // for training
    const args = [ "-g", "-q", "--noponder", "-w", weightFile, "-v", visit, "-n", "-m", randommove, "-d", "--randomtemp", randomtemp, "-r", resignrate, "--gpu", "0", "--seed", "942657784235445" ];
    
    const leela = new Controller(file, args);
    leela.start()

    // set up some settings
    await helpers.setUp(leela, komi, boardsize)
    
    for (var i = 0; i < numGame; i++){
        let prevMove = ''
        let currentMove = ''
        let gameHistory = []
        let turn = 'B'
        let gameOver = false
        let sgf = ''
        while (!gameOver) {
            // genmove, have to call await here
            await helpers.genMove(leela, turn).then(response => {
                prevMove = currentMove
                currentMove = response.content
                gameHistory.push(currentMove)
                if (turn == 'B') turn = 'W'
                else turn = 'B'
            })
            // check game over
            if (gameHistory[gameHistory.length - 1] == 'pass' && gameHistory[gameHistory.length - 2] == 'pass') {
                await helpers.finalScore(leela).then(response => {
                    gameOver = true
                    // console.log('Result: ' + response.content)
                })
            }
    
            // retrieve sgf string and write to a file
            if (gameOver) {
                await helpers.printSGF(leela).then(response => {
                    sgf = response.content
                    // write sgf to a file
                    let gameFile = sgfName + '-' + i + '.sgf'
                    fs.writeFile(gameFile, sgf, err => {
                        if (err) return console.log(err);
                    })
                    // console.log(sgf)
                })
                await leela.stop()
                break
            }
        }
    }
}

selfplay().catch(err => console.log(err))