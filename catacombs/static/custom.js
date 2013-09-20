// Create an array of images that you'd like to use
var images = [
    STATIC_URL + "com.jpg",
    STATIC_URL + "book.jpg",
    STATIC_URL + "csquare.jpg",
    STATIC_URL + "placzamkowy.jpg",
    STATIC_URL + "mermaid.jpg"
];

// Get a random number between 0 and the number of images
var randomNumber = Math.floor( Math.random() * images.length );

// Use the random number to load a random image
$.backstretch(images[randomNumber], {fade: 700});