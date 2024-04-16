const apidata = "https://nv7wn2cpz9.execute-api.us-east-1.amazonaws.com/prod/cloudresume"
const visited = document.getElementById('visited')

fetch(apidata)   
    .then(response => {
        if (!response.ok) throw new Error('invalid');
        return response.json();        
    })
    
    .then((dataArray) => {

        visited.innerHTML = dataArray
            .map(({body}) => {
                return `${body}`
            })
        
    })
    .catch(console.warn);   