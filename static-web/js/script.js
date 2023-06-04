document.getElementById('uploadForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the default form submission

  var fileInput = document.getElementById('fileInput');
  var modelSelect = document.getElementById('modelSelect');

  var file = fileInput.files[0];
  var model = modelSelect.value;

  var reader = new FileReader();

  reader.onload = function(event) {
    var fileData = event.target.result; // Binary data of the file

    // Convert the binary data to a base64-encoded string
    var base64Image = btoa(
      new Uint8Array(fileData)
        .reduce((data, byte) => data + String.fromCharCode(byte), '')
    );

    // Create a JSON object with the image, link, and filename
    var requestBody = {
      image: base64Image,
      link: model, // Use the selected Hugging Face link as the value for 'link'
      filename: file.name // Add the filename to the requestBody object
    };

    // Send the request to the Lambda function via API Gateway
    fetch('https://tyyrkrba6g.execute-api.us-west-2.amazonaws.com/apigatewaytask/', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(requestBody) // Convert the JSON object to a string
    })
      .then(function(response) {
        // Handle response from Lambda function
        console.log(response);
        // Do something with the response
      })
      .catch(function(error) {
        // Handle error
        console.error(error);
      });
  };

  reader.readAsArrayBuffer(file); // Read the file as binary data

  // Reset the form after submission
  this.reset();
});