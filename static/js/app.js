/**
 * Created by caninemwenja on 4/24/14.
 */

var marker = angular.module('FTM', []);

var transports = ['websocket', 'xhr-polling', 'jsonp-polling'];

var sock = new SockJS('http://'+window.location.host+'/marker', transports);

marker.controller('DemoController', function($scope){
    $scope.teacher = "boy likes girl";
    $scope.student = "girl likes boy";

    $scope.stemmers = [
        { label: 'Porter Stemmer', value: 'porter'},
        { label: 'Lancaster Stemmer', value: 'lancaster'},
    ]

    $scope.similarities = [
        { value: 'path', label: "Path Similarity" },
        { value: 'wup', label: 'Wu-Palmer Similarity' },
        { value: 'lch', label: 'Leacock-Chodorow Similarity'},
        { value: 'res', label: 'Resnik Similarity'},
        { value: 'jcn', label: 'Jiang-Conrath Similarity'},
        { value: 'lin', label: 'Lin Similarity'}
    ]

    $scope.scorers = [
        { value: 'min', label: 'Minimum'},
        { value: 'mean', label: 'Mean'},
    ]

    $scope.stemmer = $scope.stemmers[0];
    $scope.similarity = $scope.similarities[0];
    $scope.scoring = $scope.scorers[0];

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
            'student': $scope.student,
            'stemmer': $scope.stemmer.value,
            'similarity': $scope.similarity.value,
            'scoring': $scope.scoring.value
        }

        sock.send(JSON.stringify(data));
    };
});

//marker.filter('row_index', function(){
//   return function(, row_indices, column_indices){
//
//   };
//});