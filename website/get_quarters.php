<?php
	$db = new SQLite3('first.db');
	$statement = $db->prepare('SELECT q.quarter
	                           FROM quarters q
	                                LEFT JOIN quarters_for_courses qc ON qc.quarter_id = q.quarter_id
	                                LEFT JOIN courses c ON c.course_id = qc.course_id
	                           WHERE c.course_id = :id;');
	$statement->bindValue(':id', $_POST['course_id']);
	$results = $statement->execute();
	$ret_val = [];
	while ($row = $results->fetchArray())
	{
		array_push($ret_val, $row['quarter']);
	}
	echo json_encode($ret_val);

?>
