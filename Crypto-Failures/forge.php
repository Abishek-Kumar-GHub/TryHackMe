<?php 

$string = "admin:Mo";
$salt = "nK";
$x = crypt($string, $salt);

echo $x;
