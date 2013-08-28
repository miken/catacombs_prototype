// Create an array of images that you'd like to use
var images = [
    "/static/com.jpg",
    "/static/book.jpg",
    "/static/csquare.jpg",
    "/static/placzamkowy.jpg",
    "/static/mermaid.jpg"
];

// Get a random number between 0 and the number of images
var randomNumber = Math.floor( Math.random() * images.length );

// Use the random number to load a random image
$.backstretch(images[randomNumber], {fade: 700});