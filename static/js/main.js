

function showNewTopicForm() {
    var addNewTopicForm = document.getElementById('addNewTopicForm');
    if (addNewTopicForm.style.display === 'none') {
        addNewTopicForm.style.display = 'table-row';
    } else {
        addNewTopicForm.style.display = 'none'
    }
}

function showNewRuleForm() {
    var addNewRuleForm = document.getElementById('addNewRuleForm');
    var addNewRuleFormText = document.getElementById('addNewRuleFormText');
    var addNewRuleFormTopics = document.getElementById('addNewRuleFormTopics');
    if (addNewRuleForm.style.display === 'none') {
        addNewRuleForm.style.display = 'table-row';
        addNewRuleFormText.style.display = 'table-row';
        addNewRuleFormTopics.style.display = 'table-row';
    } else {
        addNewRuleForm.style.display = 'none';
        addNewRuleFormText.style.display = 'none';
        addNewRuleFormTopics.style.display = 'none';
    }
}

function confirmEdit() {
    return confirm('Are you sure you want to change this sentence?');
}

function confirmDelete() {
    return confirm('Are you sure you want to delete this sentence?');
}

function confirmCommentDelete() {
    return confirm('Are you sure you want to delete this comment?')
}

function confirmTopicRemoval() {
    return confirm('Are you sure you want to remove this topic?');
}

function confirmTopicEdit() {
    return confirm('Are you sure you want to change this topic?');
}

function confirmTopicDelete() {
    return confirm('Are you sure you want to delete this topic?');
}

function confirmRuleRemoval() {        
    return confirm('Are you sure you want to remove this rule?');        
}

function confirmRuleEdit() {
    return confirm('Are you sure you want to change this rule?');
}

function confirmRuleDelete() {        
    return confirm('Are you sure you want to delete this rule?');        
}

function confirmListRename() {
    return confirm('Are you sure you want to change the name of this list?');
}

function confirmListDelete() {
    return confirm('Are you sure you want to delete this list?');
}

function confirmItemRemoval() {
    return confirm('Are you sure you want to remove this item from the list?');
}

function confirmSentenceDelete() {
    return confirm('Are you sure you want to delete this sentence?');
}

function confirmSentenceEdit() {
    return confirm('Are you sure you want to change this sentence?');
}

function confirmQuestionRemove() {
    return confirm('Are you sure you want to remove this question?');
}

function submitForm() {
    document.getElementById('selectTopicForm').submit();
}

function submitListForm() {
    var selectedErrors = [];
    var checkboxes = document.querySelectorAll('.error-checkbox:checked');
    checkboxes.forEach(function(checkbox) {
        selectedErrors.push(checkbox.value);
    });
    console.log('Selected Errors: ' + selectedErrors);
    document.getElementById('selected-errors').value = selectedErrors.join(',');
    document.getElementById('manageListForm').submit();
}

// JavaScript to handle tab key press for indentation in textarea
document.addEventListener('DOMContentLoaded', function() {
    var textarea = document.getElementById('rule_text');

    if (textarea) {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                var start = this.selectionStart;
                var end = this.selectionEnd;
            
                // Set textarea value to: text before caret + tab + text after caret
                this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
            
                // Put caret at right position again
                this.selectionStart = this.selectionEnd = start + 1;
            }
        });
    }
});

function toggleAll(source) {
    const checkboxes = document.querySelectorAll('.error-checkbox');
    const selectAllCheckbox = document.getElementById('select-all');

    checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
}   


function toggleVisibility(event, id) {
    event.preventDefault();
    var elements = document.getElementsByClassName(id);
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].style.display === "none") {
        elements[i].style.display = "block";
        } else {
        elements[i].style.display = "none"
        }
    }
    
}

function showForm(id) {
    var formCell = document.getElementById(id);
    if (formCell.style.display === 'none') {
        formCell.style.display = 'block';
    } else {
        formCell.style.display = 'none';
    }
}

// Lists

function submitListDeleteForm(listType) {
    var selectedLists = [];
    if (listType === 'errorList') {
        var checkboxes = document.querySelectorAll('.error-list-checkbox:checked');
        checkboxes.forEach(function(checkbox) {
            selectedLists.push(checkbox.value);
        });
        if (selectedLists.length === 1) {
            confirm('Are you sure you want to delete this list?');
        } else {
            confirm('Are you sure you want to delete these ' + selectedLists.length + ' lists?');
        }
        console.log('Selected Lists: ' + selectedLists);
        document.getElementById('selected-lists').value = selectedLists.join(',');
        document.getElementById('deleteListsForm').submit();
    } else {
        var checkboxes = document.querySelectorAll('.cloze-list-checkbox:checked');
        checkboxes.forEach(function(checkbox) {
            selectedLists.push(checkbox.value);
        });
        if (selectedLists.length === 1) {
            confirm('Are you sure you want to delete this list?');
        } else {
            confirm('Are you sure you want to delete these ' + selectedLists.length + ' lists?');
        }
        console.log('Selected Lists: ' + selectedLists);
        document.getElementById('selected-cloze-lists').value = selectedLists.join(',');
        console.log('Form Value: ' + document.getElementById('selected-cloze-lists').value);
        document.getElementById('deleteClozeListsForm').submit();
    }
}

function submitItemForm(listType) {
    var selectedItems = [];
    if (listType === 'cloze') {
        var checkboxes = document.querySelectorAll('.sentence-checkbox:checked');
        checkboxes.forEach(function(checkbox) {
            selectedItems.push(checkbox.value);
        });
        
        var confirmMessage = (selectedItems.length === 1) ?
            'Are you sure you want to delete this sentence?' :
            'Are you sure you want to delete these ' + selectedItems.length + ' sentences?';
    } else {
        var checkboxes = document.querySelectorAll('.error-checkbox:checked');
        checkboxes.forEach(function(checkbox) {
            selectedItems.push(checkbox.value);
        });
                
        var confirmMessage = (selectedItems.length === 1) ?
            'Are you sure you want to remove this item?' :
            'Are you sure you want to remove these ' + selectedItems.length + ' items?';
    }
    var userConfirmed = confirm(confirmMessage);
    
    if (userConfirmed) {
        console.log('Selected Items: ' + selectedItems);
        document.getElementById('selected-items').value = selectedItems.join(',');
        document.getElementById('deleteItemsForm').submit();
    } else {
        console.log('Deletion canceled.')
    }
}

// Parse Sentence //

const posExplanation = document.getElementById('pos-explanation');
const morph = document.getElementById('morph');
const dependency = document.getElementById('dependency');
if (posExplanation) {
    posExplanation.innerText = 'Hover over a tag to see its explanation.';
}
if (morph) {
    morph.innerText = 'Hover over a word to see its morphology.';
}
if (dependency) {
    dependency.innerText = 'Hover over a word to see its dependency.';
}

function showText(text, id) {
    if (text.length > 0) {
        document.getElementById(id).innerText = text;
    } else {
        document.getElementById(id).innerText = '(None)';
    }
    
}


$(document).ready(function() {
    // Initialize Select2 on all select elements with the class 'select2-field'
    $('.select2-field').select2({
        placeholder: 'Select an Option',
        allowClear: true,
        minimumResultsForSearch: 1
    });

    // Focus the search input when the dropdown is opened
    $('.select2-field').on('select2:open', function() {
        // Use setTimeout to ensure the search input is available
        let searchField = document.querySelector('.select2-search__field');
        if (searchField) {
            setTimeout(function() {
                searchField.focus();
            }, 100);
        }
    });
});
