document.addEventListener("DOMContentLoaded", () => {
    
    // 4. Helper function for error handling with shake animation
    const toggleError = (elementId, errorId, hasErrorCondition) => {
        const el = document.getElementById(elementId);
        const errorEl = document.getElementById(errorId);
        
        if (hasErrorCondition) {
            errorEl.style.display = "block";
            
            // Trigger reflow to restart animation on consecutive errors
            el.classList.remove("shake");
            void el.offsetWidth;
            el.classList.add("shake");
            
            return true;
        } else {
            errorEl.style.display = "none";
            el.classList.remove("shake");
            return false;
        }
    };

    // Page 1: Sign up logic
    const nextBtn = document.getElementById("nextBtn");
    if (nextBtn) {
        // Read chatId from URL and save it to localStorage if present
        const urlParams = new URLSearchParams(window.location.search);
        const chatId = urlParams.get('chatid');
        if (chatId) {
            localStorage.setItem('chatId', chatId);
        }

        nextBtn.addEventListener("click", () => {
            const id = document.getElementById("id").value.trim();
            const name = document.getElementById("name").value.trim();
            const age = document.getElementById("age").value.trim();
            const gender = document.getElementById("gender").value;
            const location = document.getElementById("location").value.trim();
            
            let hasError = false;

            // 4. Validation with tactile Shake effect
            if (toggleError("id", "idError", !id)) hasError = true;
            if (toggleError("name", "nameError", !name)) hasError = true;
            if (toggleError("age", "ageError", !age || isNaN(age) || age <= 0)) hasError = true;
            if (toggleError("gender", "genderError", !gender)) hasError = true;
            if (toggleError("location", "locationError", !location)) hasError = true;

            if (hasError) {
                // We removed the blocking alert() because the shake animation
                // and red text are much better UX and less disruptive.
                return;
            }

            // Save data to localStorage
            const userData = { ID: id, Name: name, Age: age, Gender: gender, Location: location };
            localStorage.setItem("userData", JSON.stringify(userData));
            
            // Jump to next page
            window.location.href = "source.html";
        });
    }

    // Page 2: Source logic
    const successBtn = document.getElementById("successBtn");
    const skipBtn = document.getElementById("skipBtn");

    let saving = false;
    const completeForm = async (fromWhere) => {
        if (saving) return;
        const userData = JSON.parse(localStorage.getItem("userData") || "{}");
        if (!userData.ID || !userData.Name || !userData.Age || !userData.Gender || !userData.Location) {
            window.location.href = "index.html";
            return;
        }
        const chatId = localStorage.getItem('chatId') || crypto.randomUUID();
        localStorage.setItem('chatId', chatId);
        saving = true;
        successBtn.disabled = true;
        skipBtn.disabled = true;
        let errorEl = document.getElementById('saveError');
        if (!errorEl) {
            errorEl = document.createElement('p');
            errorEl.id = 'saveError';
            errorEl.setAttribute('role', 'alert');
            document.getElementById('sourceForm').appendChild(errorEl);
        }
        errorEl.textContent = '';
        try {
            const response = await fetch('http://localhost:8000/api/save_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userid: userData.ID,
                    name: userData.Name,
                    age: userData.Age,
                    gender: userData.Gender,
                    location: userData.Location,
                    "where it come from": fromWhere,
                    chatid: chatId
                })
            });
            const result = await response.json();
            if (!response.ok || result.status !== 'success') {
                throw new Error('Registration failed');
            }
            userData["From Where"] = fromWhere;
            localStorage.setItem('userData', JSON.stringify(userData));
            localStorage.setItem('finalDataArray', JSON.stringify([
                userData.ID, userData.Name, userData.Age, userData.Gender, userData.Location, fromWhere
            ]));
            localStorage.setItem('registeredChatId', chatId);
            window.location.href = 'core.html';
        } catch (error) {
            errorEl.textContent = 'Your details could not be saved. Please try again before starting the chat.';
        } finally {
            saving = false;
            successBtn.disabled = false;
            skipBtn.disabled = false;
        }
    };
    if (successBtn) {
        successBtn.addEventListener("click", () => {
            const source = document.getElementById("fromWhere").value;
            if (toggleError("fromWhere", "sourceError", !source)) {
                return; // Error shown and shook, stop execution
            }
            completeForm(source);
        });
    }

    if (skipBtn) {
        skipBtn.addEventListener("click", () => {
            toggleError("fromWhere", "sourceError", false); // Clear any errors
            completeForm("Skipped");
        });
    }
});
