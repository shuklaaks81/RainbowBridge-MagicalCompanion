"""
MCP Server for Rainbow Bridge Routine Management

This MCP server provides tools for managing daily routines and activities
for children with autism through the chat interface.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

logger = logging.getLogger(__name__)

class RoutineMCPServer:
    """MCP Server for routine management functionality."""
    
    def __init__(self, routine_manager, db_manager):
        self.routine_manager = routine_manager
        self.db_manager = db_manager
        self.server = Server("rainbow-bridge-routine")
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all available tools for routine management."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available routine management tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="create_routine",
                        description="Create a new daily routine for a child",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"},
                                "routine_name": {"type": "string", "description": "Name of the routine"},
                                "routine_type": {
                                    "type": "string", 
                                    "enum": ["morning", "learning", "calming", "bedtime", "custom"],
                                    "description": "Type of routine"
                                },
                                "schedule_time": {"type": "string", "description": "Time to schedule (HH:MM format)"},
                                "days": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Days of week (optional)"
                                },
                                "custom_activities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Custom activities for the routine"
                                }
                            },
                            "required": ["child_id", "routine_name", "routine_type", "schedule_time"]
                        }
                    ),
                    Tool(
                        name="get_child_routines",
                        description="Get all routines for a specific child",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"}
                            },
                            "required": ["child_id"]
                        }
                    ),
                    Tool(
                        name="start_routine",
                        description="Start a routine for a child",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"},
                                "routine_id": {"type": "integer", "description": "Routine ID to start"}
                            },
                            "required": ["child_id", "routine_id"]
                        }
                    ),
                    Tool(
                        name="complete_activity",
                        description="Mark an activity as completed in a routine",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"},
                                "routine_id": {"type": "integer", "description": "Routine ID"},
                                "activity_name": {"type": "string", "description": "Name of the activity to complete"}
                            },
                            "required": ["child_id", "routine_id", "activity_name"]
                        }
                    ),
                    Tool(
                        name="get_routine_suggestions",
                        description="Get AI-generated routine suggestions based on time and child's needs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"},
                                "time_of_day": {"type": "string", "description": "Current time of day"},
                                "child_mood": {"type": "string", "description": "Child's current mood or state"},
                                "preferred_activities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Child's preferred activities"
                                }
                            },
                            "required": ["child_id", "time_of_day"]
                        }
                    ),
                    Tool(
                        name="update_routine",
                        description="Update an existing routine",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "child_id": {"type": "integer", "description": "Child's ID"},
                                "routine_id": {"type": "integer", "description": "Routine ID to update"},
                                "updates": {
                                    "type": "object",
                                    "description": "Updates to apply to the routine"
                                }
                            },
                            "required": ["child_id", "routine_id", "updates"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls for routine management."""
            
            try:
                if name == "create_routine":
                    return await self._create_routine(arguments)
                elif name == "get_child_routines":
                    return await self._get_child_routines(arguments)
                elif name == "start_routine":
                    return await self._start_routine(arguments)
                elif name == "complete_activity":
                    return await self._complete_activity(arguments)
                elif name == "get_routine_suggestions":
                    return await self._get_routine_suggestions(arguments)
                elif name == "update_routine":
                    return await self._update_routine(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
                    
            except Exception as e:
                logger.error(f"Tool call error for {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=f"🌈 Oops! Rainbow Bridge had a little hiccup with {name}. Let's try again! ✨"
                    )]
                )
    
    async def _create_routine(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new routine using the routine manager."""
        child_id = args["child_id"]
        routine_name = args["routine_name"]
        routine_type = args["routine_type"]
        schedule_time = args["schedule_time"]
        days = args.get("days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        custom_activities = args.get("custom_activities", [])
        
        try:
            # Get template activities based on routine type
            if routine_type == "custom" and custom_activities:
                activities = custom_activities
            else:
                # Use predefined template activities
                template_activities = self.routine_manager.routine_templates.get(routine_type, [])
                activities = [activity["name"] for activity in template_activities]
                
                # Add any custom activities
                if custom_activities:
                    activities.extend(custom_activities)
            
            # Create the routine
            routine = await self.routine_manager.create_routine(
                child_id=child_id,
                name=routine_name,
                activities=activities,
                schedule_time=schedule_time,
                days_of_week=days
            )
            
            # Format response for the child
            response_text = f"""🌈 Wonderful! I've created your new colorful routine called "{routine_name}"! ✨

📅 **Schedule:** {schedule_time} on {', '.join(days)}

🎨 **Activities in your routine:**
"""
            for i, activity in enumerate(routine.activities, 1):
                response_text += f"{i}. {activity.name} ({activity.duration_minutes} minutes) {activity.visual_cue}\n"
            
            response_text += f"\n🎉 Your routine is ready to start! I'll remind you when it's time. Rainbow Bridge is excited to go on this adventure with you!"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"🌈 I had trouble creating your routine, but don't worry! Let's try again with Rainbow Bridge magic! ✨"
                )]
            )
    
    async def _get_child_routines(self, args: Dict[str, Any]) -> CallToolResult:
        """Get all routines for a child."""
        child_id = args["child_id"]
        
        try:
            routines = await self.routine_manager.get_child_routines(child_id)
            
            if not routines:
                response_text = "🌈 You don't have any routines yet! Would you like Rainbow Bridge to help you create a colorful new routine? ✨"
            else:
                response_text = "🌈 Here are all your wonderful routines! ✨\n\n"
                for routine in routines:
                    status = "✅ Active" if routine.active else "💤 Paused"
                    response_text += f"**{routine.name}** {status}\n"
                    response_text += f"📅 Scheduled: {routine.schedule_time}\n"
                    response_text += f"🎨 Activities: {len(routine.activities)} colorful activities\n"
                    response_text += f"📝 Days: {', '.join(routine.days_of_week)}\n\n"
                
                response_text += "Would you like to start any of these routines or create a new one? 🌟"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🌈 I'm having trouble finding your routines, but Rainbow Bridge is here to help! Let's try again! ✨"
                )]
            )
    
    async def _start_routine(self, args: Dict[str, Any]) -> CallToolResult:
        """Start a routine for a child."""
        child_id = args["child_id"]
        routine_id = args["routine_id"]
        
        try:
            # Get the routine
            routine = await self.routine_manager.get_routine(routine_id)
            if not routine or routine.child_id != child_id:
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text="🌈 I couldn't find that routine! Let's look at your available routines together! ✨"
                    )]
                )
            
            # Start the routine
            await self.routine_manager.start_routine(routine_id)
            
            # Create encouraging response
            response_text = f"🌈 Let's start your '{routine.name}' routine! This is going to be a wonderful colorful adventure! ✨\n\n"
            response_text += "🎯 **First Activity:**\n"
            
            if routine.activities:
                first_activity = routine.activities[0]
                response_text += f"🎨 **{first_activity.name}** ({first_activity.duration_minutes} minutes)\n"
                response_text += f"📝 {first_activity.description}\n\n"
                
                if first_activity.instructions:
                    response_text += "📋 **Steps:**\n"
                    for i, instruction in enumerate(first_activity.instructions, 1):
                        response_text += f"  {i}. {instruction}\n"
                
                response_text += f"\n🌟 When you're done, tell Rainbow Bridge you completed '{first_activity.name}'!"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🌈 Let's try starting your routine again! Rainbow Bridge believes in you! ✨"
                )]
            )
    
    async def _complete_activity(self, args: Dict[str, Any]) -> CallToolResult:
        """Mark an activity as completed."""
        child_id = args["child_id"]
        routine_id = args["routine_id"]
        activity_name = args["activity_name"]
        
        try:
            # Mark activity as completed
            success = await self.routine_manager.complete_activity(routine_id, activity_name)
            
            if success:
                # Get next activity
                routine = await self.routine_manager.get_routine(routine_id)
                next_activity = None
                
                for i, activity in enumerate(routine.activities):
                    if activity.name == activity_name and i + 1 < len(routine.activities):
                        next_activity = routine.activities[i + 1]
                        break
                
                if next_activity:
                    response_text = f"🎉 Amazing job completing '{activity_name}'! You're doing wonderful! ✨\n\n"
                    response_text += "🎯 **Next Activity:**\n"
                    response_text += f"🎨 **{next_activity.name}** ({next_activity.duration_minutes} minutes)\n"
                    response_text += f"📝 {next_activity.description}\n\n"
                    
                    if next_activity.instructions:
                        response_text += "📋 **Steps:**\n"
                        for i, instruction in enumerate(next_activity.instructions, 1):
                            response_text += f"  {i}. {instruction}\n"
                else:
                    response_text = f"🌈 Fantastic! You completed '{activity_name}' and finished your entire routine! 🎉\n\n"
                    response_text += "🌟 You did an amazing job today! Rainbow Bridge is so proud of you! ✨"
            else:
                response_text = "🌈 I couldn't mark that activity as complete, but that's okay! Let's try again! ✨"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🌈 Great job on your activity! Let's continue with Rainbow Bridge magic! ✨"
                )]
            )
    
    async def _get_routine_suggestions(self, args: Dict[str, Any]) -> CallToolResult:
        """Get AI-generated routine suggestions."""
        child_id = args["child_id"]
        time_of_day = args["time_of_day"]
        child_mood = args.get("child_mood", "")
        preferred_activities = args.get("preferred_activities", [])
        
        try:
            # Use the AI assistant to generate suggestions
            from core.ai_assistant import SpecialKidsAI
            ai_assistant = SpecialKidsAI()
            
            suggestions = await ai_assistant.generate_routine_suggestions(
                child_id=child_id,
                current_activities=preferred_activities,
                time_of_day=time_of_day
            )
            
            response_text = f"🌈 Rainbow Bridge has some wonderful activity suggestions for you! ✨\n\n"
            
            for i, suggestion in enumerate(suggestions, 1):
                response_text += f"🎨 **{i}. {suggestion['title']}**\n"
                response_text += f"📝 {suggestion['description']}\n"
                response_text += f"⏰ Duration: {suggestion['duration']}\n\n"
            
            response_text += "Would you like to create a routine with any of these colorful activities? 🌟"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🌈 Let Rainbow Bridge think of some wonderful activities for you! ✨"
                )]
            )
    
    async def _update_routine(self, args: Dict[str, Any]) -> CallToolResult:
        """Update an existing routine."""
        child_id = args["child_id"]
        routine_id = args["routine_id"]
        updates = args["updates"]
        
        try:
            success = await self.routine_manager.update_routine(routine_id, updates)
            
            if success:
                response_text = "🌈 Perfect! I've updated your routine with beautiful new colors! Your routine is now even more magical! ✨"
            else:
                response_text = "🌈 I had trouble updating your routine, but don't worry! Rainbow Bridge will help you make it perfect! ✨"
            
            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🌈 Let's work together to make your routine even more wonderful! ✨"
                )]
            )

# Global server instance
routine_mcp_server = None

def create_routine_mcp_server(routine_manager, db_manager) -> RoutineMCPServer:
    """Create and return the routine MCP server instance."""
    global routine_mcp_server
    routine_mcp_server = RoutineMCPServer(routine_manager, db_manager)
    return routine_mcp_server

async def run_routine_mcp_server(routine_manager, db_manager):
    """Run the routine MCP server."""
    server_instance = create_routine_mcp_server(routine_manager, db_manager)
    
    # Run with stdio transport
    async with stdio_server(
        server_instance.server,
        StdioServerParameters()
    ) as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, write_stream, InitializationOptions(
                server_name="rainbow-bridge-routine",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )
