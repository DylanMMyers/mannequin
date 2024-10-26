import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.118/build/three.module.js';

import {FBXLoader} from 'https://cdn.jsdelivr.net/npm/three@0.118.1/examples/jsm/loaders/FBXLoader.js';
import {GLTFLoader} from 'https://cdn.jsdelivr.net/npm/three@0.118.1/examples/jsm/loaders/GLTFLoader.js';
import {OrbitControls} from 'https://cdn.jsdelivr.net/npm/three@0.118/examples/jsm/controls/OrbitControls.js';

// Create a clock for tracking time
const clock = new THREE.Clock();

// Initialize scene, camera, and renderer
const scene = new THREE.Scene();

// ## CAMERA
//const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
const fov = 60;
const aspect = 1920 / 1080;
const near = 1.0;
const far = 1000.0;
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
camera.position.set(75, 20, 0);

// ### RENDERER
const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate ); // calls the animation function (at bottom) on each frame
document.body.appendChild(renderer.domElement);

// ### CONTROLS
const controls = new OrbitControls(camera, renderer.domElement); 
controls.target.set(0, 20, 0);
controls.update();

// ### LIGHTING
let light = new THREE.DirectionalLight(0xFFFFFF, 1.0);
light.position.set(20, 100, 10);
light.target.position.set(0, 0, 0);
light.castShadow = true;
light.shadow.bias = -0.001;
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;
light.shadow.camera.near = 0.1;
light.shadow.camera.far = 500.0;
light.shadow.camera.near = 0.5;
light.shadow.camera.far = 500.0;
light.shadow.camera.left = 100;
light.shadow.camera.right = -100;
light.shadow.camera.top = 100;
light.shadow.camera.bottom = -100;
scene.add(light);

light = new THREE.AmbientLight(0xFFFFFF, 4.0);
scene.add(light);

// ############ ADD OBJECTS ##################

// Platform for model to "stand" on
const plane = new THREE.Mesh(
    new THREE.PlaneGeometry(100, 100, 10, 10),
    new THREE.MeshStandardMaterial({
        color: 0x202020,
    }));
plane.castShadow = false;
plane.receiveShadow = true;
plane.rotation.x = -Math.PI / 2;
scene.add(plane);

// ############## LOAD IN MODELS ################
let mixers = [];

const loader = new FBXLoader();
const anim = new FBXLoader();
let mannequinModel;

loader.load('./Assets/AnimatedMannequin/MannequinModel.fbx', function(fbxModel) {
    fbxModel.scale.setScalar(0.1);
    mannequinModel = fbxModel;
    console.log("Loaded fbx");
    scene.add(fbxModel);

    // Load animation after the model is loaded
    anim.load('./Assets/AnimatedMannequin/DanceAnimation.fbx', function(animationFbx) {
        const mixer = new THREE.AnimationMixer(fbxModel);
        mixers.push(mixer);

        const animation = animationFbx.animations[0];
        const action = mixer.clipAction(animation);
        action.play();
    }, undefined, function(error) {
        console.log("Failed to load animation:");
        console.error(error);
    });
}, undefined, function(error) {
    console.log("Failed to load model:");
    console.error(error);
});

// ########## TAKE IN PARAMETERS FROM HTML ##################
// Global torsoSize variable to hold the value from the form
let torsoSize = 10; // Default value
let legSize = 10;
let armSize = 10;

// Function to handle size updates from the HTML form
export function handleSizes(updatedLegSize, updatedArmSize, updatedTorsoSize) {
    console.log("Received sizes:");
    console.log("Leg Size:", updatedLegSize);
    console.log("Arm Size:", updatedArmSize);
    console.log("Torso Size:", updatedTorsoSize);

    // Update the global torsoSize variable
    torsoSize = parseFloat(updatedTorsoSize) || 10; // Set a default if input is invalid
    legSize = parseFloat(updatedLegSize) || 10;
    armSize = parseFloat(updatedArmSize) || 10;
}


/// ############## RENDER LOOP #####################
function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    for (const mixer of mixers) {
        mixer.update(delta);
    }

    renderer.render(scene, camera);
}

animate();