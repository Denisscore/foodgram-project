// Дополнительная валидация формы на tags
function checkboxCheck(tags) {
    for (var i = 0; i < tags.length; i++) {
        if (tags[i].checked) return true
    }
    alert("Добавте тег")
    return false;
}


// Дополнительная валидация формы на ingredient
function ingredientCheck(nameIngredient) {
    if (0 < nameIngredient.length) return true
    alert("Добавте ингридиент")
    return false;
}


