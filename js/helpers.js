async function setUp (leela, komi, boardsize) {
    // set komi for engine
    try {
        response = await leela.sendCommand({name: 'komi', args: [komi]})
    } catch (err) {
        throw new Error('Failed to send command!')
    }

    // set boardsize
    try {
        response = await leela.sendCommand({name: 'boardsize', args: [boardsize]})
    } catch (err) {
        throw new Error('Failed to send command!')
    }
    return true
}

async function playMove(leela, turn, move) {
    // genmove
    try {
        response = await leela.sendCommand({name: 'play', args: [turn, move]})
    } catch (err) {
        throw new Error('Failed to send command!')
    }

    if (response.error) {
        throw new Error('Command not understood by Leela!')
    }
    return response
}

async function genMove(leela, turn) {
    // genmove
    try {
        response = await leela.sendCommand({name: 'genmove', args: [turn]})
    } catch (err) {
        throw new Error('Failed to send command!')
    }

    if (response.error) {
        throw new Error('Command not understood by Leela!')
    }
    return response
}

async function finalScore(leela) {
    try {
        response = await leela.sendCommand({name: 'final_score'})
    } catch (err) {
        throw new Error('Failed to send command!')
    }

    if (response.error) {
        throw new Error('Command not understood by Leela!')
    }
    return response
}

async function printSGF(leela) {
    try {
        response = await leela.sendCommand({name: 'printsgf'})
    } catch (err) {
        throw new Error('Failed to send command!')
    }

    if (response.error) {
        throw new Error('Command not understood by Leela!')
    }
    return response
}

module.exports.setUp = setUp;
module.exports.playMove = playMove;
module.exports.genMove = genMove;
module.exports.finalScore = finalScore;
module.exports.printSGF = printSGF;