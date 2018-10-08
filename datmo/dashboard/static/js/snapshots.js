$(document).ready(function(){
  var toggle = {};
  $('table.sortable th').on('click', function(e){
    var target = e.target.tagName == 'TH' ? e.target : e.target.parentNode;
    var th = target;
    var sortable_column = 0;
    while((target = target.previousSibling) != null) sortable_column++;
    sortable_column = ((sortable_column+1)/2)-1;

    Array.prototype.slice.call(th.parentNode.children).forEach(n => {
      n.classList = ['grid-header-sort'];
    });
    // toggle sort
    if (typeof toggle[sortable_column] === 'undefined'){
      toggle[sortable_column] = true;
    } else {
      toggle[sortable_column] = !toggle[sortable_column];
    }
    th.classList = ['grid-header-sort-' + (toggle[sortable_column] ? 'desc' : 'asc') + ' grid-header-sort'];

    var table, rows, switching, i, x, y, shouldSwitch;
    table = $(e.target).parents('table')[0];
    switching = true;
    /*Make a loop that will continue until
    no switching has been done:*/
    while (switching) {
      //start by saying: no switching is done:
      switching = false;
      rows = table.getElementsByTagName("TR");
      /*Loop through all table rows (except the
      first, which contains table headers):*/
      for (i = 1; i < (rows.length - 1); i++) {
        //start by saying there should be no switching:
        shouldSwitch = false;
        /*Get the two elements you want to compare,
        one from current row and one from the next:*/
        x = rows[i].getElementsByTagName("TD")[sortable_column];
        y = rows[i + 1].getElementsByTagName("TD")[sortable_column];

        //check if the two rows should switch place:
        if (x && toggle[sortable_column] && x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          //if so, mark as a switch and break the loop:
          shouldSwitch= true;
          break;
        } else  if (x && !toggle[sortable_column] && x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          shouldSwitch= true;
          break;
        }
      }
      if (shouldSwitch) {
        /*If a switch has been marked, make the switch
        and mark that a switch has been done:*/
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
      }
    }
  });
  var git_url;
  $('table.sortable .snapshot-diff input').on('click', function(e){
    if (!git_url){
      var table = $(e.target).parents('table')[0];
      console.log(table);
      if (table && table.dataset.giturl){
        git_url = table.dataset.giturl;
      }
    }

    var elem1 = Array.prototype.slice.call($('table.sortable .snapshot-diff input:checked'), -1)[0];
    var elem2 = Array.prototype.slice.call($('table.sortable .snapshot-diff input:checked'), -2)[0];
    if ($('table.sortable .snapshot-diff input:checked').length>=2){
      if (elem1 && elem2){
        var diff_url = window.location.pathname + '/diff/' +  elem1.dataset.snapshotid + '/' + elem2.dataset.snapshotid;
        window.open(diff_url, '_blank');
        setTimeout(function(){
          elem1.checked = false;
          elem2.checked = false;
        }, 300);
      }
    }
  })
});