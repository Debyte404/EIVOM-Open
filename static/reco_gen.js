// console.log(movdata);
// console.log(typeof movdata);
console.log(movdata[0]['Title']);


movdata.forEach(item => {
    console.log(item)
    let title = item.Title;
    let movie_poster = item.Poster;
    let retard = item.Rated;
    let release = item.Released;
    let imdbID = item.imdbID;
    let rating = item.imdbRating;
    let plot = item.Plot;

    console.log(title)
    var cards = document.getElementById('result-list')
    cards.innerHTML +=`<div class="card_rec">
        <div class="contain_left">
            <div class="external-link"><i data-id="${imdbID}" class="fa fa-external-link" aria-hidden="true" onclick="showDetails(this)"></i></div>
            <img src="${movie_poster}">
            <div class="movietitle_container">
                <div class="full-title">${title}</div>
                <div class="movietitle">${title}</div>
            </div>
        </div>
        <div class="right-grid">
            <div class="grid-item">
                <p style="color:navy"><i class="fa fa-star" aria-hidden="true"></i> ${rating}</p>
                <p>${release.split(" ")[2]}</p>
                <p>${retard}</p>
            </div>
            <div class="grid-item">
                <h2>${title}</h2>

                    <p>
                    ${plot}
                    </p>

            </div>
            </div>

    </div>`
    
    // cards.innerHTML += `<div class="card_rec">
//     <div class="contain_left">
//         <img src="${movie_poster}">
//         <div class="movietitle_container">
//             <div class="full-title">${title}</div>
//             <div class="movietitle">${title}</div>
//         </div>
//     </div>
// </div>`
    // const li = document.createElement('li');
    // li.textContent = item;
    // resultList.appendChild(li);
    // resultList.innerHTML += "";
});
