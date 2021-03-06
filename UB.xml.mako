<%
	from rllab.misc.mako_utils import compute_rect_vertices
	ring_friction = 0.000
	eu_friction = 0.000
	detector_friction = 0.005
	eu_height = 0.2
	detector_width = 0.1
	detector_height = 1.0
	ring_radius = 0.5
	origin = 2.0
%>

<box2d>
	<world timestep="0.05" gravity="0,0">
		<body name="ring" type="dynamic" position="0,${ring_radius}">
			<fixture
			  density="5"
			  friction="${ring_friction}"
			  shape="circle"
			  radius="${ring_radius}"
			/>
		</body>
		<body name="eu_cradle" type="dynamic" position="0,${origin}">
			<fixture
			  density="5"
			  friction="${ring_friction}"
			  shape="polygon"
			  vertices="${compute_rect_vertices((0,origin),(0,eu_height+origin),eu_height/2.0)}"
			/>
		</body>
		
		<body name="detector" type="dynamic" position="10,10">
			<fixture
			  density="1"
			  friction="${detector_friction}"
			  shape="polygon" vertices="${compute_rect_vertices((10,10),(10,10+detector_height),detector_width/2)}"
			/>
		</body>
		
		<body name="x_track" type="static" position="0,${ring_radius}">
			<fixture friction="${ring_friction}" group="-1" shape="polygon" box="180,0.1"/>
		</body>
		<body name="y_track" type="static" position="180,${origin}">
			<fixture friction="${eu_friction}" group="-1" shape="polygon" box="360,0.1"/>
		</body>
		<body name="pivot" type="static" position="10,10">
			<fixture friction="${detector_friction}" group="-1" shape="circle" radius="0.01"/>
		</body>
		
		<joint type="prismatic" name="xaxis" bodyA="x_track" bodyB="ring"/>
		<joint type="prismatic" name="yaxis" bodyA="y_track" bodyB="eu_cradle"/>
		<joint type="revolute" name="angular_axis" bodyA="pivot" bodyB="detector"/>
		<state type="xpos" body="ring"/>
		<state type="xpos" body="eu_cradle"/>
		<state type="apos" body="detector"/>
		
	</world>
</box2d>
