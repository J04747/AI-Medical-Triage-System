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

    const completeForm = (fromWhere) => {
        const storedData = localStorage.getItem("userData");
        let userData = storedData ? JSON.parse(storedData) : {};
        
        userData["From Where"] = fromWhere;
        
        // Final structure: ["ID", "Name", "Age", "Gender", "Location", "From Where"]
        const dataArray = [
            userData.ID || "N/A", 
            userData.Name || "N/A", 
            userData.Age || "N/A", 
            userData.Gender || "N/A", 
            userData.Location || "N/A", 
            userData["From Where"]
        ];

        console.log("Final Data Array:", dataArray);
        
        // Save the data to localStorage so core.html can access it
        localStorage.setItem("finalDataArray", JSON.stringify(dataArray));
        localStorage.setItem("userData", JSON.stringify(userData));
        
        // Jump to core page
        window.location.href = "core.html";
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
