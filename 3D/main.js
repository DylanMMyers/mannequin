import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';
import {OBJLoader} from 'three/examples/jsm/loaders/OBJLoader.js';

// Initialize scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
const light = new THREE.AmbientLight(0xf3eee3, 1.5); // soft white light
scene.add( light );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

// Load 3D model
const loader = new GLTFLoader();
let woodMannequin;

loader.load( './Models/scene.gltf', function ( gltf ) {
    const model = gltf.scene;
    scene.add(gltf.scene);
    woodMannequin = model;
    woodMannequin.scale.set(10, 10, 10);  // Default scale
    console.log("OBJECT SUCCESSFULLY ADDED");
}, undefined, function (error) {
    console.error(error);
});


//// ###### MULTI PART ATTEMPT #####
// const loader = new GLTFLoader();
// let torso;
// loader.load( './multiGLTF/torso.gltf', function (gltf){
//     scene.add(gltf.scene);
//     torso = gltf.scene;
//     console.log("torso added");
// }, undefined, function (error){
//     console.log("torso failed");
//     console.error(error);
// });
// let leftArm;
// loader.load( './multiGLTF/leftArm.gltf', function (gltf){
//     scene.add(gltf.scene);
//     leftArm = gltf.scene;
//     console.log("leftArm added");
// }, undefined, function (error){
//     console.log("leftArm failed");
//     console.error(error);
// });

// const loader = new FBXLoader();
// let mannequinModel;

// loader.load( './fbx/Mannequin/Mannequin_Animation.FBX', function(fbxModel){
//     scene.add(fbxModel);
//     mannequinModel = fbxModel;
//     console.log("Loaded fbx");
// }, undefined, function (error){
//     console.log("Failed to load fbx:");
//     console.error(error);
// }
// );

// const loader = new OBJLoader();
// let mannequinModel;

// loader.load( './obj/boneMannequin.obj', function(objModel){
//     scene.add(objModel);
//     mannequinModel = objModel;
//     console.log("Loaded obj");
// }, undefined, function (error){
//     console.log("Failed to load obj:");
//     console.error(error);
// }
// );




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

camera.position.z = 2; // 2
camera.position.y = 1; // 1
camera.position.x = 0; // 0
camera.rotation.y = 0; // 0

// Animation loop
function animate() {
    if (woodMannequin) {
        woodMannequin.rotation.y += 0.01;

        // Use the updated torsoSize value to scale the mannequin
        woodMannequin.scale.set(legSize, torsoSize, armSize);
    } else {
        console.log("Missing mannequin");
    }

    // if (mannequinModel){
    //     mannequinModel.scale.set(10, torsoSize, 10);
    //     mannequinModel.rotation.y += 0.01;
    // }else{
    //     console.log("Missing mannequin");
    // }

    renderer.render(scene, camera);
}
