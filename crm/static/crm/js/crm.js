var table;
var myDataRef;
var auth;

$(document).ready(function() {
    table = $('#table_id').DataTable({
      "columnDefs": [
        {
            "targets": [ 0 ],
            "visible": false,
            "searchable": false
        }
      ]
    });
    initFirebase();
} );

function getListDr(eventId) {
    return myDataRef.child('events/' + eventId + '/list');
}

   
function initFirebase() {
    console.log('init firebase');
    myDataRef = new Firebase('https://guestflow.firebaseio.com/');
    auth = new FirebaseSimpleLogin(myDataRef, function(error, user) {
        if (error) {
            // an error occurred while attempting login
            console.log(error);
        } else if (user) {
            // user authenticated with Firebase
            console.log('User ID: ' + user.id + ', Provider: ' + user.provider + ', Name: ' + user.email);
            myDataRef.child('users/' + user.id + '/events').on('child_added', function(eventSnapshot) {
                //TODO multi event support
                myDataRef.child('users/' + user.id + '/events/' + eventSnapshot.name()).on('value', function(valueSnapshot) {
                    if (valueSnapshot.val() == true) {
                        actEvent = valueSnapshot.name();
                        initHandlers(actEvent);
                    } else {
                        auth.logout();
                    }
                });
            });
        } else {
            // user is logged out
            console.log('logged out');
            // TODO remove hardcoded login
            auth.login('password', {
                email : 'a@test.sk',
                password : '',
            });
        }
    });
}

//TODO move to common    
function setDefault(obj, attr, defaultVal) {
    if (obj[attr] == undefined) {
        obj[attr] = defaultVal;
    }
}

//TODO move to common
function setGuestDefaults(data) {
    setDefault(data, 'firstname', '');
    setDefault(data, 'lastname', '');
    setDefault(data, 'custom1', '');
    setDefault(data, 'custom2', '');
    setDefault(data, 'note', '');
    setDefault(data, 'accomp', 0);
    setDefault(data, 'accompChecked', 0);

    return data;
}


function initHandlers(eventId) {   
    console.log('initializing handlers for event: ' + eventId);
    listDr = getListDr(eventId);
    listDr.on('value', function(snapshot) {
        if (snapshot.val() != null) {
            // list is loaded
            console.log('List loaded');
            table.draw();
            // if (!doNotSort) {
                // sortList();
            // }
            // doNotSort = false;
        }
    });
        
    listDr.on('child_added', function(snapshot) {
      addGuestLcl(snapshot.name(), setGuestDefaults( snapshot.val() ));
    });
    
    listDr.on('child_changed', function(snapshot) {
      updateGuestLcl( snapshot.name(), setGuestDefaults( snapshot.val() ));
      // doNotSort = true;
    });
}
    
function addGuestLcl(id, guest) {
    console.log('adding guest locally');
    table.row.add( [
       id,
       guest.firstname,
       guest.lastname,
       guest.custom1,
       guest.custom2,
       guest.accomp,
       // guest.accompChecked,
    ] );
};
    
function updateGuestLcl(id, data) {
    console.log('updating guest locally');
}
    
