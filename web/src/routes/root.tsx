import { CirclePlay, Dumbbell, Home } from "lucide-react";
import { Link, Outlet } from "react-router-dom";

import {
	Sidebar,
	SidebarContent,
	SidebarGroup,
	SidebarGroupContent,
	SidebarGroupLabel,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarProvider,
} from "@/components/ui/sidebar";

const items = [
	{
		title: "Home",
		url: "/",
		icon: Home,
	},
	{
		title: "Live View",
		url: "/live",
		icon: CirclePlay,
	},
	{
		title: "Training View",
		url: "/training",
		icon: Dumbbell,
	},
];

export const Root = () => {
	return (
		<SidebarProvider>
			<Sidebar>
				<SidebarContent>
					<SidebarGroup>
						<SidebarGroupLabel>Application</SidebarGroupLabel>
						<SidebarGroupContent>
							<SidebarMenu>
								{items.map((item) => (
									<SidebarMenuItem key={item.title}>
										<SidebarMenuButton asChild>
											<Link to={item.url}>
												<item.icon />
												<span>{item.title}</span>
											</Link>
										</SidebarMenuButton>
									</SidebarMenuItem>
								))}
							</SidebarMenu>
						</SidebarGroupContent>
					</SidebarGroup>
				</SidebarContent>
			</Sidebar>
			<main className="size-full">
				<Outlet />
			</main>
		</SidebarProvider>
	);
};

export default Root;
