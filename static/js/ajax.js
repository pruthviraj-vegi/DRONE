const limit = 30;
let start = 0;
let action = "inactive";
let sort_column;
let sort_order = "Dec";
let tableBody = $("#table_body");



function getAllSearchParams() {
    let params = new URLSearchParams();
    const form = document.getElementById('search-form');


    if (form) {
        const formData = new FormData(form);
        formData.forEach((value, key) => {
            if (typeof value === 'string' && value.trim() !== '') {
                params.append(key, value);
            } else if (value) {
                params.append(key, value);
            }
        });
    }
    // Add limit, start, and sorting parameters
    if (typeof limit !== "undefined") params.append("limit", limit);
    if (typeof start !== "undefined") params.append("start", start);
    if (typeof sort_column !== "undefined")
        params.append("sort_column", sort_column);
    if (typeof sort_order !== "undefined") params.append("sort_type", sort_order);

    // Add hidden content parameter
    if (typeof hidden_content !== "undefined" && hidden_content === false) {
        params.append("hidden_content", hidden_content);
    }

    return params;
}

if (typeof search_url !== "undefined") {

    function load_post_data() {
        // sourcery skip: avoid-using-var
        let params = getAllSearchParams();
        let requestData = {};

        // Convert URLSearchParams to plain object
        for (let [key, value] of params) {
            requestData[key] = value;
        }

        $.ajax({
            url: search_url,
            method: "GET",
            data: requestData,
            cache: false,
            success: function (response) {
                // Check for empty string, empty array, or "No data found" in HTML
                if (
                    !response ||
                    (Array.isArray(response) && response.length === 0) ||
                    (typeof response === "string" && (response.trim() === "" || response.includes("No data found")))
                ) {
                    // Display "No data found" message
                    if (start === 0) {
                        // Only show message on first load or search reset
                        tableBody.html('<tr><td colspan="9" class="text-center">No data found</td></tr>');
                    }
                    action = "end"; // No more data to load
                    return;
                }
                tableBody.append(response);
                action = "inactive";
            },
        });
    }

    load_post_data();

    $(window).scroll(function () {
        const { scrollHeight, scrollTop, clientHeight } = document.documentElement;
        if (
            scrollTop + clientHeight >= scrollHeight - 150 &&
            action == "inactive"
        ) {
            action = "active";
            start += limit;
            load_post_data();
        }
    });

    $("#table__data").on("click", ".sort-link", function (e) {
        e.preventDefault();
        $("#table_body").empty();
        const column = $(this).data("column");
        sort_column = column;
        reverse(sort_column);
        start = 0;
        load_post_data();
    });

    function table_reset() {
        tableBody.empty();
        start = 0;
        load_post_data();
    }

    $(document).on("submit", "#search-form", function (e) {
        e.preventDefault();
        table_reset();

    });

    $(document).on("submit", "#custom_search", function (e) {
        e.preventDefault();
        table_reset();
    });
}

// console.log("height", scrollHeight, "scrollTop", scrollTop, "clientHeight", clientHeight);