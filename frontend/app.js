async function getLeads(){

const token = localStorage.getItem("token")

const res = await fetch("http://localhost:5000/leads",{

headers:{
"Authorization":"Bearer " + token
}

})

const leads = await res.json()

const table = document.getElementById("leadsTable")

table.innerHTML = ""

leads.forEach(lead => {

const row = `
<tr>
<td>${lead.name}</td>
<td>${lead.status}</td>
<td>${lead.priority}</td>
</tr>
`

table.innerHTML += row

})

}