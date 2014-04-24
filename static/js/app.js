/**
 * Created by caninemwenja on 4/24/14.
 */

var marker = angular.module('FTM', []);

var transports = ['websocket', 'xhr-polling', 'jsonp-polling'];

var sock = new SockJS('http://'+window.location.host+'/marker', transports);

marker.controller('DemoController', function($scope){
    $scope.teacher = "boy likes girl";
    $scope.student = "girl likes boy";

    sock.onopen = function(){
        console.log("Connection opened");
    };

    sock.onclose = function(){
        console.log("Connection closed");
    };

    sock.onmessage = function(e){
        console.log("Data received: "+JSON.stringify(e.data));

        var data = JSON.parse(e.data);

        console.log(data);

        $scope.result = data;
        $scope.$apply();
    };

    $scope.sendMsg = function(){

        var data = {
            'teacher': $scope.teacher,
            'student': $scope.student
        }

        sock.send(JSON.stringify(data));
    };
});

//marker.filter('row_index', function(){
//   return function(, row_indices, column_indices){
//
//   };
//});