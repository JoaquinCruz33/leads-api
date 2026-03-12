const API_URL = "https://real-estate-crm.onrender.com"


// ============================
// LOGIN
// ============================

async function login(){

const email = document.getElementById("email").value
const password = document.getElementById("password").value

const res = await fetch(API_URL + "/login",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
email: email,
password: password
})
})

const data = await res.json()

if(data.error){
alert(data.error)
return
}

localStorage.setItem("access_token", data.access_token)

window.location.href = "dashboard.html"

}


// ============================
// REGISTER
// ============================

async function register(){

const name = document.getElementById("name").value
const email = document.getElementById("email").value
const password = document.getElementById("password").value

const res = await fetch(API_URL + "/register",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
name:name,
email:email,
password:password
})
})

const data = await res.json()

alert(data.message || data.error)

if(data.message){
window.location.href="index.html"
}

}


// ============================
// CREAR LEAD
// ============================

async function createLead(){

const token = localStorage.getItem("access_token")

const name = document.getElementById("lead_name").value
const email = document.getElementById("lead_email").value
const phone = document.getElementById("lead_phone").value
const intent = document.getElementById("intent").value
const budget = document.getElementById("budget").value
const timeline = document.getElementById("timeline").value

const res = await fetch(API_URL + "/leads",{

method:"POST",

headers:{
"Content-Type":"application/json",
"Authorization":"Bearer " + token
},

body:JSON.stringify({
name:name,
email:email,
phone:phone,
intent:intent,
budget:budget,
timeline:timeline
})

})

const data = await res.json()

alert(data.message)

getLeads()

}


// ============================
// OBTENER LEADS
// ============================

async function getLeads(){

const token = localStorage.getItem("access_token")

const res = await fetch(API_URL + "/leads",{

headers:{
"Authorization":"Bearer " + token
}

})

const leads = await res.json()

const table = document.getElementById("leadsTable")

if(!table) return

table.innerHTML=""

leads.forEach(lead=>{

const row = `
<tr>
<td>${lead.name}</td>
<td>${lead.email}</td>
<td>${lead.phone}</td>
<td>${lead.priority}</td>
<td>${lead.status}</td>
</tr>
`

table.innerHTML += row

})

}


// ============================
// EXPORTAR EXCEL
// ============================

function exportLeads(){

const token = localStorage.getItem("access_token")

window.open(API_URL + "/export?token=" + token)

}


// ============================
// LOGOUT
// ============================

function logout(){

localStorage.removeItem("access_token")

window.location.href="index.html"

}


// ============================
// PROTEGER DASHBOARD
// ============================

function protectDashboard(){

const token = localStorage.getItem("access_token")

if(!token){
window.location.href="index.html"
}

}


// ============================
// AUTOLOAD DASHBOARD
// ============================

window.onload = function(){

if(window.location.pathname.includes("dashboard")){

protectDashboard()

getLeads()

}

}