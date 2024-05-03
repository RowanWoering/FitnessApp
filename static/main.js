

const loginBtn = document.getElementById('login');
const signupBtn = document.getElementById('signup');

login_page = signupBtn.parentNode.classList.contains('slide-up')
signup_page= loginBtn.parentNode.parentNode.classList.contains('slide-up')

loginBtn.addEventListener('click', (e) => {
	console.log('hi')
	let parent = e.target.parentNode.parentNode;
	console.log(parent)
	if(signup_page){
		Array.from(e.target.parentNode.parentNode.classList).find((element) => {
			if(element !== "slide-up") {
				parent.classList.add('slide-up')
				console.log('a')
			}else{
				signupBtn.parentNode.classList.add('slide-up')
				parent.classList.remove('slide-up')
				console.log('b')
			}
		});
		signup_page = false
		login_page = true
	}


});

signupBtn.addEventListener('click', (e) => {
	let parent = e.target.parentNode;
	if(login_page){
		Array.from(e.target.parentNode.classList).find((element) => {
			if(element !== "slide-up") {
				parent.classList.add('slide-up')
			}else{
				loginBtn.parentNode.parentNode.classList.add('slide-up')
				parent.classList.remove('slide-up')
			}
		});
		signup_page=true
		login_page=false
	}

});