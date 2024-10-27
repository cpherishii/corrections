
function updateExerciseImage() {
    const exerciseImage = document.getElementById("exercise-image");
    const selectedOption = document.querySelector('input[name="exercise"]:checked').value;
    console.log("Exercise ID: " + selectedOption);
    
    exerciseImage.innerHTML = "";
    
    let imageSource;
    switch (selectedOption) {
        case "1":
            imageSource = "static/images/exercises/correct_or_incorrect.jpg";
            break;
        case "2":
            imageSource = "static/images/exercises/choose_the_correct_sentence.jpg";
            break;
        case "3":
            imageSource = "static/images/exercises/correct_the_sentence.jpg";
            break;
        case "4":
            imageSource = "static/images/exercises/mix_it_up.jpg";
            break;
        default:
            imageSource = "static/images/exercises/correct_or_incorrect.jpg";
    }
    
    if (imageSource) {
        const img = document.createElement("img");
        img.src = imageSource;
        img.alt = "Exercise Image";
        exerciseImage.appendChild(img);
    }
}

const exerciseOptions = document.getElementById('exercise');
if (exerciseOptions) {
    document.getElementById("exercise").addEventListener("change", updateExerciseImage);
    window.onload = updateExerciseImage;
}

function displayLoadingMessage(loadingMessage) {
    document.getElementById(loadingMessage).style.display = 'block';
}

const errorExerciseForm = document.getElementById('errorExerciseForm');
if (errorExerciseForm) {
    document.getElementById('errorExerciseForm').addEventListener('submit', function() {
        displayLoadingMessage('loadingMessage1');
    });
}

const clozeExerciseForm = document.getElementById('clozeExerciseForm');
if (clozeExerciseForm) {
    document.getElementById('clozeExerciseForm').addEventListener('submit', function() {
        displayLoadingMessage('loadingMessage2');
    });
}

const verbFormExerciseForm = document.getElementById('verbFormExerciseForm');
if (verbFormExerciseForm) {
    document.getElementById('verbFormExerciseForm').addEventListener('submit', function() {
        displayLoadingMessage('loadingMessage3');
    });
}

function toggleAllTopics(source) {
    const checkboxes = document.querySelectorAll('input[name="topics"]');
    const selectAllCheckbox = document.getElementById('select-all');

    checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
}

function showExerciseForm(hideId, showId) {
    var toHide = document.getElementById(hideId);
    var toShow = document.getElementById(showId);
    toHide.style.display = 'none';
    toShow.style.display = 'block';
}

// Exercises //

let isCorrect = false;
let isFeedbackShowing = false;
let firstAttempt = true;
let correctAnswer = false;
let isInputBlurred = false;

let attempts = parseInt(sessionStorage.getItem('attempts')) || 0;
let points = parseFloat(sessionStorage.getItem('points')) || 0;
let score = attempts > 0 ? (points / attempts * 100).toFixed(2) : 0;

console.log("Attempts: " + attempts);
console.log("Points: " + points);

const scoreDisplay = document.getElementById('score');
if (scoreDisplay) {
    document.getElementById('score').innerText = 'Your Score: ' + score + "%";
}

function updateScore() {
    score = (points / attempts * 100).toFixed(2);
    document.getElementById('score').innerText = 'Your Score: ' + score + '%';
}

function showBackgroundColor(isCorrect) {
    const backgroundColor = isCorrect ? 'rgb(195, 249, 207)' : 'rgb(252, 213, 213)';
    document.getElementById('exercise-div').style.backgroundColor = backgroundColor;
}

function showFeedbackMessage(message) {
    document.getElementById('feedback-message').innerText = message;
    document.getElementById('feedback').style.display = 'block';
}

// Correct of Incorrect //

function correctOrIncorrect(buttonValue, showCorrect) {
    let feedbackMessage = "";
    console.log("Show correct: " + showCorrect);
    console.log("Button pressed: " + buttonValue);

    document.getElementById('sentence').style.display = 'none';
    document.getElementById('colored-sentence').style.display = 'block';
    document.getElementById('error').style.display = 'block';
    document.getElementById('buttons').style.display = 'none';

    isFeedbackShowing = true;
    if (showCorrect) {
        if (buttonValue === 'correct') {
            feedbackMessage = "Yes, this sentence is correct!";
            points += 1;
            isCorrect = true;
        } else {
            feedbackMessage = "Actually, this sentence is correct.";
            isCorrect = false;
        }
    } else {
        document.getElementById('corrections').style.display = 'block';
        if (buttonValue === 'incorrect') {
            feedbackMessage = "You're right! This sentence is incorrect.";
            points += 1;
            isCorrect = true;
        } else {
            feedbackMessage = "Sorry, but this sentence is incorrect.";
            isCorrect = false;
        }
    }

    attempts++;
    showBackgroundColor(isCorrect);
    showFeedbackMessage(feedbackMessage);
    updateScore();

    console.log("Is Correct: " + isCorrect);
    console.log("Attempts: " + attempts);
    console.log("Points: " + points);
}

// Choose the Correct Sentence //

function chooseTheCorrectSentence(buttonValue, correctFirst) {
    let feedbackMessage = "";
    console.log("Correct first: " + correctFirst);
    console.log("Button pressed: " + buttonValue);

    document.getElementById('sentence-options').style.display = 'none';
    document.getElementById('colored-sentences').style.display = 'block';
    document.getElementById('error').style.display = 'block';

    isFeedbackShowing = true;

    if (correctFirst) {
        if (buttonValue === 'a') {
            feedbackMessage = "Yes, the first sentence is correct!";
            points += 1;
            isCorrect = true;
        } else {
            feedbackMessage = "Sorry, the first sentence is the correct one.";
            isCorrect = false;
        }
    } else {
        if (buttonValue === 'b') {
            feedbackMessage = "Yes, the second sentence is correct!";
            points += 1;
            isCorrect = true;
        } else {
            feedbackMessage = "Sorry, the second sentence is the correct one.";
            isCorrect = false;
        }
    }

    attempts++;
    showBackgroundColor(isCorrect);
    showFeedbackMessage(feedbackMessage);
    updateScore();
}

// Correct the Sentence //

function correctTheSentence(correctSentences) {
    var userInput = document.getElementById('correction-input').value.trim();
    console.log("Correct sentences: " + correctSentences);
    console.log("Submitted sentence: " + userInput);
    let feedbackMessage = "";
    let correctSentence = "";

    if (correctSentences.includes(userInput)) {
        feedbackMessage = "Correct! Well Done!";
        correctSentence = userInput;
        var error = document.getElementById('error');
        error.style.display = 'block';
        document.getElementById('correct-sentence').innerText = correctSentence;
        document.getElementById('correct-sentence').style.display = 'block';
        document.getElementById('input-div').style.display = 'none';
        points += 1;
        correctAnswer = true;
    } else {
        feedbackMessage = "Sorry, try again.";
        firstAttempt = false;
        correctAnswer = false;
    }
    if (firstAttempt && correctAnswer) {
        isCorrect = true;
    }

    attempts++;
    document.getElementById('correction-input').blur();
    isInputBlurred = true;

    showBackgroundColor(correctAnswer);
    showFeedbackMessage(feedbackMessage);
    updateScore();
}


// Cloze Exercise //

function initializeClozeExercise(missingWords, clozedSentence, originalSentences) {
    let missingWordIndex = 0;
    let sentenceMatch = false;

    document.addEventListener('keydown', function(event) {
        let key = event.key;
        if (key >= '1' && key <= '9') {
            let linkId = 'link-' + key;
            let linkElement = document.getElementById(linkId);
            if (linkElement) {
                linkElement.click();
            }
        }
    });

    document.querySelectorAll('.word-link').forEach(function(element) {
        element.replaceWith(element.cloneNode(true));
    });

    document.querySelectorAll('.word-link').forEach(function(element) {
        element.addEventListener('click', function(event) {
            event.preventDefault();
            var word = this.getAttribute('data-word');
            checkWord(word);
        })
    });

    function checkWord(word) {
        console.log("Check word called with: " + word);
        console.log("Missing words: " + missingWords);
        var selectedWord = word;
        let feedbackMessage = "";
        if (missingWords[missingWordIndex].includes(selectedWord)) {
            var missingWordDisplay = document.getElementById('missing-word-' + missingWordIndex)
            if (missingWords.length > missingWordIndex + 1) {
                missingWordDisplay.style.visibility = 'visible';
                missingWordDisplay.innerText = selectedWord + '  /';
                feedbackMessage = "Correct! Now choose the next word.";
                clozedSentence = clozedSentence.replace("____", selectedWord);
                console.log("Completed sentence so far: " + clozedSentence);
                points++;
                console.log("Points: " + points);
                missingWordIndex++;
            } else {
                clozedSentence = clozedSentence.replace("____", selectedWord).toLowerCase();
                console.log("Complete clozed sentence: " + clozedSentence);
                for (let i = 0; i < originalSentences.length; i++) {
                    let lowerSentence = originalSentences[i].toLowerCase();
                    console.log("Lower case sentence: " + lowerSentence);
                    if (clozedSentence === lowerSentence) {
                        sentenceMatch = true;
                        sentenceToDisplay = originalSentences[i];
                        console.log("Sentence to display: " + sentenceToDisplay);
                    }
                }
                if (sentenceMatch) {
                    feedbackMessage = "Correct! Well Done!";
                    clozedSentence = clozedSentence.replace("____", selectedWord);
                    missingWordDisplay.style.visibility = 'visible';
                    missingWordDisplay.innerText = selectedWord;
                    var clozedSentenceDisplay = document.getElementById('clozed-sentence');
                    var originalSentence = document.getElementById('original-sentence');
                    clozedSentenceDisplay.style.display = 'none';
                    originalSentence.style.display = 'block';
                    originalSentence.innerText = sentenceToDisplay;
                    points++;
                    correctAnswer = true;
                    showBackgroundColor(correctAnswer);
                    console.log("Attempts: " + attempts);
                    console.log("Points: " + points);
                    document.getElementById('target-words').style.display = 'none';
                }
            } 
        } else {
            feedbackMessage = 'Sorry, try again.';
            firstAttempt = false;
            showBackgroundColor(correctAnswer);
            console.log("Attempts: " + attempts);
            console.log("Points: " + points);
        }
        if (firstAttempt && correctAnswer) {
            isCorrect = true;
        }

        attempts++;
        showFeedbackMessage(feedbackMessage);
        isFeedbackShowing = true;
        updateScore();
    }
}

// Verb-Form Exercise //

let outerLoopIndex = 0;

const verbFormsTable = document.getElementById('verb-forms-table');
if (verbFormsTable) {
    var verbFormLinks = verbFormsTable.querySelectorAll('div.options-' + outerLoopIndex + ' > a');


    document.addEventListener('keydown', function(event) {
        let key = event.key;
        if (key >= '1' && key <= verbFormLinks.length) {
            let linkId = 'verb-form-link-' + outerLoopIndex + key;
            let linkElement = document.getElementById(linkId);
            if (linkElement) {
                linkElement.click();
            }
        }
    });
}

function checkVerbForm(verbFormId, wordList, divId) {
    console.log('Verb Form ID: ' + verbFormId)
    console.log('Div ID: ' + divId);
    var answer = wordList[0].toLowerCase();
    console.log('Answer: ' + answer);
    var verbForm = document.getElementById(verbFormId).textContent.trim().toLowerCase();
    console.log('Verb Form: ' + verbForm);
    console.log('Number of verb forms: ' + numVerbForms);
    let feedbackMessage = "";

    if (verbForm === answer) {
        document.getElementById('answer-' + divId).style.display = 'block';
        document.getElementById('options-' + divId).style.display = 'none';
        if (numVerbForms > 1) {
            feedbackMessage = "Correct! Now choose the next word.";
            document.getElementById('exercise-div').style.backgroundColor = 'white';
            numVerbForms -= 1;
            points++;
            outerLoopIndex += 1;
        } else {
            feedbackMessage = "Correct! Well Done!";
            isCorrect = true;
            showBackgroundColor(isCorrect);
            points++;
        }
        
    } else {
        document.getElementById(verbFormId).style.color = 'red';
        if (wordList.length > 3) {
            feedbackMessage = 'Sorry, try again.';
        } else {
            if (verbFormId[verbFormId.length-1] === '0') {
                var correctIndex = 1;
            } else {
                var correctIndex = 0;
            }
            feedbackMessage = 'Not quite!';
            document.getElementById('verb-form-link-' + divId + '-' + correctIndex).style.color = 'green';
        }
        
        showBackgroundColor(isCorrect);
    }

    attempts++;
    showFeedbackMessage(feedbackMessage);
    updateScore();
}

function storeValues() {
    document.getElementById('result').value = isCorrect ? 'correct' : 'incorrect';
    sessionStorage.setItem('attempts', attempts);
    sessionStorage.setItem('points', points);
}

function resetSession() {
    sessionStorage.removeItem('attempts');
    sessionStorage.removeItem('points');
    attempts = 0;
    points = 0;
    score = 0;
    document.getElementById('score').innerText = 'Your Score: ' + score + '%';
}

function showError() {
    var error = document.getElementById('error');
    error.style.display = 'block';
    error.scrollIntoView();
}

const nextButton = document.getElementById('next-button');
if (nextButton) {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'ArrowRight') {
            if (isFeedbackShowing || isInputBlurred) {
                event.preventDefault();
                document.getElementById('next-button').click();
            }
        }
    });
}

const greenButton = document.getElementById('green-button');
const redButton = document.getElementById('red-button');

if (greenButton){
    document.addEventListener('keydown', function(event) {
        if (event.key === 'c') {
            document.getElementById('green-button').click();
        }
    });
}

if (redButton) {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'i') {
            document.getElementById('red-button').click();
        }
    });
}

const aLink = document.getElementById('a-link');
const bLink = document.getElementById('b-link');

if (aLink) {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'a') {
                document.getElementById('a-link').click();
        }
    });
}

if (bLink) {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'b') {
            document.getElementById('b-link').click();
        }
    });
}

const input = document.getElementById('correction-input');
const checkButton = document.getElementById('check-button');

if (input) {
    input.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            document.getElementById('check-button').click();
        }
    });
    
    input.addEventListener('blur', function(event) {
        isInputBlurred = true;
    });

    input.addEventListener('focus', function(event) {
        isInputBlurred = false;
    });
}


