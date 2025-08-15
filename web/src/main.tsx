import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import "@/main.css";
import Live from "@/routes/live";
import Root from "@/routes/root";
import Training from "@/routes/training";

const router = createBrowserRouter([
	{
		path: "/",
		element: <Root />,
		children: [
			{
				path: "live",
				element: <Live />,
			},
			{
				path: "training",
				element: <Training />,
			},
		],
	},
]);

// biome-ignore-start lint/style/noNonNullAssertion: see index.html
createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<RouterProvider router={router} />
	</StrictMode>,
);
// biome-ignore-end lint/style/noNonNullAssertion: see index.html
