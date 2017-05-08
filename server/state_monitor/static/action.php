<?php

$time=$_POST['curtime'];
$data = mt_rand(10,100);
$response = array(
	'data'=>$data
);
echo json_encode($response);
?>