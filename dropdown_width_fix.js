// Fix dropdown menu width
document.addEventListener('DOMContentLoaded', function() {
    // Get all dropdown menus
    var dropdownMenus = document.querySelectorAll('.dropdown-menu');
    
    // Apply width fixes
    dropdownMenus.forEach(function(menu) {
        // Set width to auto
        menu.style.width = 'auto';
        menu.style.maxWidth = 'fit-content';
        
        // Fix list items
        var listItems = menu.querySelectorAll('li');
        listItems.forEach(function(item) {
            item.style.width = 'auto';
            item.style.maxWidth = 'fit-content';
            
            // Fix links
            var link = item.querySelector('a');
            if (link) {
                link.style.width = 'auto';
                link.style.maxWidth = 'fit-content';
            }
        });
    });
});
