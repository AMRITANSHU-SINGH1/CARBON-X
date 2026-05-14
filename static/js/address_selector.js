document.addEventListener("DOMContentLoaded", function() {
    const stateDistrictMap = {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore"],
        "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
        "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Noida"],
        "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri"]
    };

    const stateSelect = document.getElementById("state-select");
    const districtSelect = document.getElementById("district-select");

    if (stateSelect && districtSelect) {
        const prefillDistrict = districtSelect.getAttribute("data-prefill");
        let prefillState = null;

        if(prefillDistrict) {
            for(const [state, districts] of Object.entries(stateDistrictMap)) {
                if(districts.includes(prefillDistrict)) {
                    prefillState = state;
                    break;
                }
            }
            // If district was custom/not in map, we can optionally add it
            if (!prefillState) {
                stateDistrictMap["Other"] = [prefillDistrict];
                prefillState = "Other";
            }
        }

        stateSelect.innerHTML = '<option value="" disabled selected>-- Select State --</option>';
        for (const state of Object.keys(stateDistrictMap)) {
            const option = document.createElement("option");
            option.value = state;
            option.textContent = state;
            if(state === prefillState) option.selected = true;
            stateSelect.appendChild(option);
        }

        const populateDistricts = () => {
            const selectedState = stateSelect.value;
            districtSelect.innerHTML = '<option value="" disabled selected>-- Select District --</option>';
            
            if (selectedState && stateDistrictMap[selectedState]) {
                const districts = stateDistrictMap[selectedState];
                for (const district of districts) {
                    const dOption = document.createElement("option");
                    dOption.value = district;
                    dOption.textContent = district;
                    districtSelect.appendChild(dOption);
                }
            }
        };

        stateSelect.addEventListener("change", populateDistricts);

        // Pre-fill fields if we are editing
        if (prefillState) {
            populateDistricts();
            districtSelect.value = prefillDistrict;
        }
    }
});
