document.addEventListener('DOMContentLoaded', function() {
    populateBoxes();
});

async function fetchFromAPI() {
    try {
        const response = await fetch('/api/table');
        const data = await response.json();
        console.log(data)
        return data;
    } catch (error) {
        console.error('Error fetching boxes:', error);
        return [];
    }
}

async function populateBoxes() {
    const data = await fetchFromAPI();
    const container = document.getElementById("course-category");
    console.log(data)
    
    let boxHTML = ''; // Initialize an empty string to store the HTML
    
    data.forEach((boxData, index) => {

        const box = `
        <div class="course-model">
            <h2>course Name : ${boxData[0]}</h2>
            <p><strong>Price:</strong>${boxData[1]}</p>
            <p><strong>Rating:</strong> ${boxData[2]}</p>
        </div>
        `;
        
        boxHTML += box; // Append the HTML to the programsHTML string
    });
    
    container.innerHTML = boxHTML; // Set the innerHTML once after the loop completes
};