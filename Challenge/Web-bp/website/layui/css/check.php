<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>登录检测</title>
  <meta name="renderer" content="webkit">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <link rel="stylesheet" href="layui/css/layui.css"  media="all">
  <style>
  </style>
</head>
<body>
<div id="d"><div>
<script>
  var r = {code: 'bugku10000'}
  if(r.code == 'bugku10000'){
        console.log('e');
	document.getElementById('d').innerHTML = "Wrong account or password!";
  }else{
        console.log('0');
        window.location.href = 'success.php?code='+r.code;
  }
  
  </script>
</body>
</html>
